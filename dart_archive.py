"""Archive-only media identification and persistent ingest manifest."""

import getpass
import csv
import io
import json
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path

from dart_storage import atomic_bytes, atomic_json

MANIFEST_NAME = "DART_archive_only.json"
DEFAULT_THRESHOLD_MB = 50
MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp", ".webp",
    ".pdf", ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm",
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma",
}


def parse_private_prefixes(value):
    if not isinstance(value, str):
        raise ValueError("Private filename prefixes must be text separated by semicolons.")
    prefixes = tuple(part.strip() for part in value.replace("\n", ";").split(";") if part.strip())
    if any("/" in prefix or "\\" in prefix or "\0" in prefix for prefix in prefixes):
        raise ValueError("Private filename prefixes must not contain path separators.")
    return prefixes


def is_private(path, prefixes):
    return bool(prefixes) and Path(path).name.startswith(prefixes)


def is_private_csv_filename(filename, prefixes):
    return is_private(filename, prefixes) or (
        filename.startswith("_") and is_private(filename[1:], prefixes)
    )


def private_csv_path(core_csv, collection_id):
    if not isinstance(core_csv, (str, Path)) or not str(core_csv).strip():
        raise ValueError("Configure the public core metadata CSV in the SHOW collection's _data directory.")
    core = Path(core_csv)
    if not core.is_absolute() or core.suffix.lower() != ".csv" or not core.is_file():
        raise ValueError("The public core metadata CSV must be an existing absolute .csv path.")
    path = core.with_name(f"PRIVATE_{core.name}")
    if (path.parent.name != "_data" or path.parent.parent.name != collection_id
            or path.parent.parent.parent.name != "collections" or not path.parent.is_dir()):
        raise ValueError("The public core metadata CSV must be inside collections/<collection-id>/_data.")
    if any(part.is_symlink() for part in (core, path, path.parent, path.parent.parent, path.parent.parent.parent)):
        raise ValueError("The CSVs and SHOW collection directories must not be symlinks.")
    if path.resolve() == core.resolve():
        raise ValueError("The private metadata CSV must be a separate, non-symlink file.")
    return path


def split_private_objects(objects, parents, prefixes):
    private = [obj for obj in objects if is_private(obj["filename"], prefixes)]
    public = [obj for obj in objects if not is_private(obj["filename"], prefixes)]
    by_id = {parent["objectid"]: parent for parent in parents}
    descendants = {parent["objectid"]: [] for parent in parents}
    for obj in public:
        parent_id = obj.get("parentid")
        seen = set()
        while parent_id in by_id and parent_id not in seen:
            seen.add(parent_id)
            descendants[parent_id].append(obj)
            parent_id = by_id[parent_id].get("parentid")
    public_parents = []
    for parent in parents:
        children = descendants[parent["objectid"]]
        if not children:
            continue
        safe_parent = dict(parent)
        if safe_parent.get("first_child_filename") not in {child["filename"] for child in children}:
            first = sorted(children, key=lambda child: child["filename"])[0]["filename"]
            safe_parent["first_child_filename"] = first
            if safe_parent.get("type") == "multiple":
                safe_parent["display_text_base"] = Path(first).stem
        public_parents.append(safe_parent)
    return public, private, public_parents


def write_private_csv(path, columns, rows):
    if not rows:
        return
    columns = [column for column in columns if column != "filepath"]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    atomic_bytes(path, output.getvalue().encode("utf-8"))


def threshold_bytes(value):
    if isinstance(value, bool):
        raise ValueError("archive-only-file-threshold must be a positive whole number of MB")
    try:
        number = int(value)
    except (ValueError, TypeError):
        raise ValueError("archive-only-file-threshold must be a positive whole number of MB") from None
    if str(value).strip() != str(number) or number <= 0:
        raise ValueError("archive-only-file-threshold must be a positive whole number of MB")
    return number * 1_000_000


def is_archive_only(path, threshold):
    path = Path(path)
    content_type, _ = mimetypes.guess_type(path.name)
    is_media = (path.suffix.lower() in MEDIA_EXTENSIONS
                or bool(content_type and (content_type == "application/pdf"
                                         or content_type.startswith(("image/", "audio/", "video/")))))
    return is_media and path.stat().st_size > threshold_bytes(threshold)


def classify_sources(objects, auxiliary, threshold, core_titles):
    entries = []
    archive_paths = set()
    for obj in objects:
        path = Path(obj["filepath"])
        if is_archive_only(path, threshold):
            obj["archive_only"] = True
            obj["display_template"] = "record"
            archive_paths.add(str(path))
            entries.append({
                "path": path, "objectid": obj["objectid"],
                "new_filename": obj.get("azure_object_id", obj["objectid"]) + path.suffix,
                "title": obj.get("title") or core_titles.get(obj["objectid"], ""),
            })
    retained = []
    for obj in auxiliary:
        path = Path(obj["source"])
        if is_archive_only(path, threshold):
            entries.append({
                "path": path, "objectid": obj["objectid"],
                "new_filename": obj["azure_object_id"] + path.suffix,
                "title": obj.get("title", ""),
            })
        else:
            retained.append(obj)
    return entries, archive_paths, retained


def record_archive_files(directory, entries, collection_id, version):
    """Atomically merge source references; never replace malformed existing evidence."""
    if not entries:
        return
    path = Path(directory) / MANIFEST_NAME
    if path.is_symlink():
        raise ValueError(f"Archive manifest must not be a symlink: {path}")
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            records = json.load(handle)
        if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
            raise ValueError(f"Invalid archive manifest: {path}")
    else:
        records = []
    existing = {}
    for record in records:
        try:
            key = (record["original_path"], record["objectid"], record["new_filename"])
        except KeyError as exc:
            raise ValueError(f"Invalid archive manifest record in {path}: missing {exc.args[0]}") from exc
        if key in existing:
            raise ValueError(f"Duplicate archive manifest record in {path}: {key}")
        existing[key] = record
    for entry in entries:
        source = Path(entry["path"])
        size = source.stat().st_size
        original_path = os.path.abspath(source)
        key = (original_path, entry["objectid"], entry["new_filename"])
        record = existing.get(key)
        if record is None:
            record = {"created_at": datetime.now(timezone.utc).isoformat()}
            records.append(record)
            existing[key] = record
        record.update({
            "originating_file_name": source.name,
            "original_path": original_path,
            "objectid": entry["objectid"],
            "new_filename": entry["new_filename"],
            "title": entry.get("title", ""),
            "file_size_bytes": size,
            "username": getpass.getuser(),
            "dart_version": version,
            "collection_slug": collection_id,
        })
    atomic_json(path, records)
