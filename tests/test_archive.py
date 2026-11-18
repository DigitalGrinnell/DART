import json
import csv
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

import app
import dart_archive
import dart_linux
from dart_processing import build_export_rows, get_display_template
from dart_service import JobService
from unittest.mock import patch


class ArchiveTests(unittest.TestCase):
    def test_restricted_media_and_large_media_export(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = ("small audio.MP3", "large.webm", "large.wav", "small.jpg", "unknown.aiff")
            for name in names:
                path = root / name
                with path.open("wb") as stream:
                    stream.truncate(1_000_001 if name.startswith("large") else 1)
            objects = [{"filepath": str(root / name), "filename": name,
                        "objectid": str(index), "display_template": "transcript"}
                       for index, name in enumerate(names)]
            entries, paths, _ = dart_archive.classify_sources(objects, [], 1, True)
            columns, rows = build_export_rows(["objectid", "original_file_name"], objects, [])
            by_name = {row["original_file_name"]: row for row in rows}
            for name, template in (("small audio.MP3", "audio"), ("large.webm", "video"),
                                   ("large.wav", "audio"), ("unknown.aiff", "audio")):
                with self.subTest(name=name):
                    self.assertIn(str(root / name), paths)
                    self.assertEqual(root.joinpath(name).as_uri(), by_name[name]["file_UUID"])
                    self.assertEqual("", by_name[name]["object_location"])
                    self.assertEqual(template, by_name[name]["display_template"])
            self.assertNotIn(str(root / "small.jpg"), paths)
            self.assertIn("file_UUID", columns)
            self.assertEqual(4, len(entries))
            self.assertEqual("audio", get_display_template(".aiff"))

    def test_large_audio_is_audio_without_restriction(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "large.mp3"
            small = Path(directory) / "small.mp4"
            small.write_bytes(b"video")
            with source.open("wb") as stream:
                stream.truncate(1_000_001)
            obj = {"filepath": str(source), "filename": source.name, "objectid": "id",
                   "display_template": "transcript"}
            small_obj = {"filepath": str(small), "filename": small.name, "objectid": "small",
                         "display_template": "video"}
            _, paths, _ = dart_archive.classify_sources([obj, small_obj], [], 1)
            self.assertEqual("audio", obj["display_template"])
            self.assertNotIn("file_UUID", obj)
            self.assertNotIn(str(small), paths)
            self.assertEqual("video", small_obj["display_template"])

    def test_restricted_ohm_media_sibling_is_not_retained_for_upload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sibling.mov"
            path.write_bytes(b"video")
            sibling = {"source": str(path), "objectid": "id", "azure_object_id": "sibling"}
            entries, _, retained = dart_archive.classify_sources([], [sibling], 50, True)
            self.assertEqual([], retained)
            self.assertEqual("restricted media", entries[0]["status"])
            self.assertEqual("sibling.mov", entries[0]["new_filename"])

    def test_private_prefixes_and_nested_compounds(self):
        prefixes = dart_archive.parse_private_prefixes("PRIVATE-; restricted-\nSECRET-")
        self.assertTrue(dart_archive.is_private("PRIVATE-note.docx", prefixes))
        self.assertTrue(dart_archive.is_private("restricted-1.pdf", prefixes))
        self.assertFalse(dart_archive.is_private("private-note.docx", prefixes))
        self.assertTrue(dart_archive.is_private_csv_filename("_PRIVATE-note.jpg", prefixes))
        self.assertTrue(dart_archive.is_private_csv_filename("_secret.jpg", ("_secret",)))
        objects = [
            {"objectid": "p", "filename": "PRIVATE-note.jpg", "parentid": "nested"},
            {"objectid": "a", "filename": "public.jpg", "parentid": "nested"},
            {"objectid": "b", "filename": "SECRET-hidden.pdf", "parentid": "private-parent"},
        ]
        parents = [
            {"objectid": "root", "first_child_filename": "PRIVATE-note.jpg", "type": "compound"},
            {"objectid": "nested", "parentid": "root", "first_child_filename": "PRIVATE-note.jpg",
             "display_text_base": "PRIVATE-note", "type": "multiple"},
            {"objectid": "private-parent", "first_child_filename": "SECRET-hidden.pdf", "type": "compound"},
        ]
        public, private, kept = dart_archive.split_private_objects(objects, parents, prefixes)
        self.assertEqual(["a"], [row["objectid"] for row in public])
        self.assertEqual({"p", "b"}, {row["objectid"] for row in private})
        self.assertEqual({"root", "nested"}, {row["objectid"] for row in kept})
        self.assertTrue(all(row["first_child_filename"] == "public.jpg" for row in kept))
        self.assertEqual("public", next(row for row in kept if row["objectid"] == "nested")["display_text_base"])

    def test_private_csv_destination_and_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "collections" / "test" / "_data"
            data.mkdir(parents=True)
            core = data / "test_metadata.csv"
            core.write_text("public metadata")
            private = data / "PRIVATE_test_metadata.csv"
            self.assertEqual(private, dart_archive.private_csv_path(core, "test"))
            for path, collection in ((core, "other"), (Path(directory) / "missing.csv", "test"),
                                     (Path(directory) / "test_metadata.csv", "test")):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    dart_archive.private_csv_path(path, collection)
            other = data / "a different name.CSV"
            other.write_text("public")
            self.assertEqual(data / "PRIVATE_a different name.CSV",
                             dart_archive.private_csv_path(other, "test"))
            dart_archive.write_private_csv(private, ["objectid", "filepath"], [{"objectid": "one", "filepath": "secret"}])
            dart_archive.write_private_csv(private, ["objectid"], [{"objectid": "two"}])
            with private.open(newline="") as stream:
                self.assertEqual([{"objectid": "two"}], list(csv.DictReader(stream)))
            dart_archive.write_private_csv(private, ["objectid"], [])
            self.assertEqual("objectid\r\ntwo\r\n", private.read_bytes().decode())
            private.unlink()
            private.symlink_to(core)
            with self.assertRaises(ValueError):
                dart_archive.private_csv_path(core, "test")
            self.assertEqual("public metadata", core.read_text())

    def test_headless_commands_and_submission_are_disabled(self):
        with patch("sys.argv", ["dart_linux.py", "--env-file", "/not-read", "--list-jobs"]):
            self.assertEqual(2, dart_linux.main())
        with self.assertRaisesRegex(RuntimeError, "currently disabled"):
            JobService.submit(object.__new__(JobService), "operator", "export", {})
        root = Path(__file__).resolve().parents[1]
        for script in ("accept_headless_batch.py", "run_headless_pipeline.py"):
            result = subprocess.run([sys.executable, str(root / "scripts" / script)],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(2, result.returncode)
            self.assertIn("currently disabled", result.stderr)

    def test_threshold_is_strict_and_applies_only_to_media(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.JPG"
            with path.open("wb") as stream:
                stream.truncate(50_000_000)
            self.assertFalse(dart_archive.is_archive_only(path, 50))
            with path.open("ab") as stream:
                stream.write(b"x")
            self.assertTrue(dart_archive.is_archive_only(path, 50))
            pdf_client = Mock()
            ok, message = app.upload_to_azure(pdf_client, str(path), "assets/objs/test", "test_dg_1", ".JPG")
            self.assertFalse(ok)
            self.assertIn("upload refused", message)
            pdf_client.get_blob_client.assert_not_called()
            archive = path.with_suffix(".zip")
            path.rename(archive)
            self.assertFalse(dart_archive.is_archive_only(archive, 50))
            media = path.with_suffix(".svg")
            archive.rename(media)
            self.assertTrue(dart_archive.is_archive_only(media, 50))
        for invalid in (0, -1, True, 1.5, "", "nan"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                dart_archive.threshold_bytes(invalid)

    def test_archive_only_entries_explain_the_configured_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            media = Path(directory) / "large.jpg"
            with media.open("wb") as stream:
                stream.truncate(1_000_001)
            entries, archive_paths, retained = dart_archive.classify_sources(
                [{"filepath": str(media), "objectid": "test_dg_1"}], [], 1
            )
            self.assertEqual("larger than 1 MB threshold", entries[0]["status"])
            self.assertEqual({str(media)}, archive_paths)
            self.assertEqual([], retained)

    def test_manifest_is_persistent_idempotent_and_rejects_bad_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "source.pdf"
            media.write_bytes(b"example")
            entry = {"path": media, "objectid": "test_dg_1", "new_filename": "test_dg_1.pdf",
                     "status": "larger than 50 MB threshold"}
            dart_archive.record_archive_files(root, [entry], "test", "1.0")
            manifest = root / dart_archive.MANIFEST_NAME
            first = json.loads(manifest.read_text())
            dart_archive.record_archive_files(root, [entry], "test", "1.0")
            self.assertEqual(first, json.loads(manifest.read_text()))
            record = first[0]
            self.assertEqual(str(media), record["original_path"])
            self.assertEqual("source.pdf", record["originating_file_name"])
            self.assertEqual("test_dg_1.pdf", record["new_filename"])
            self.assertEqual(("larger than 50 MB threshold", 7, "test", "1.0"),
                             (record["status"], record["file_size_bytes"], record["collection_slug"], record["dart_version"]))
            self.assertNotIn("title", record)
            self.assertTrue(record["created_at"])
            self.assertTrue(record["username"])
            manifest.write_text("{bad")
            with self.assertRaises(ValueError):
                dart_archive.record_archive_files(root, [entry], "test", "1.0")
            self.assertEqual("{bad", manifest.read_text())
