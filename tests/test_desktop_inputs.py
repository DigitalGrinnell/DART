import csv
import json
import os
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import app
import dart_archive
from dart_processing import derivative_source_exports


class DesktopInputsTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        for folder in ("first", "second"):
            directory = self.inputs / folder
            directory.mkdir()
            (directory / f"{folder}.jpg").write_bytes(b"fixture")
        self.core = self.root / "core.csv"
        self.core.write_text("objectid,original_file_name,parentid,title,type,filepath\n")
        self.stack.enter_context(patch.object(app, "PERSISTENCE_FILE", self.root / "persistent.json"))
        self.stack.enter_context(patch.object(app, "setup_desktop_logging"))
        self.stack.enter_context(patch.object(app, "setup_working_dir_logging"))
        self.settings = dict(app.DEFAULT_APP_SETTINGS, core_metadata_csv=str(self.core),
                             **{"collection-id": "test", "create_multiple_objects": False})
        self.stack.enter_context(patch.object(app, "load_app_settings",
                                            side_effect=lambda _: (self.settings, "")))
        self.stack.enter_context(patch.object(app, "save_app_settings", return_value=(True, "saved")))
        preferences = app.PersistentStorage()
        preferences.set_ui_state("last_input_dir", str(self.inputs))
        preferences.set_ui_state("last_output_dir", str(self.root))

    def start_page(self, initially_unavailable=False):
        page = Mock(spec=app.ft.Page)
        page.window = SimpleNamespace()
        page.session = SimpleNamespace(generated_ids=set())
        page.overlay = []
        page.controls = []
        page.theme = None
        page.dark_theme = None
        page.add.side_effect = lambda *controls: page.controls.extend(controls)
        original_exists = Path.exists

        def exists(path):
            return False if initially_unavailable and path == self.inputs else original_exists(path)

        with patch.object(Path, "exists", exists):
            app.main(page)
        return page

    def walk(self, controls):
        for control in controls:
            yield control
            yield from self.walk(control._get_children())

    def execute(self, page, function):
        selector = next(control for control in self.walk(page.controls)
                        if isinstance(control, app.ft.Dropdown)
                        and control.label == "Select Function to Execute")
        selector.on_change(SimpleNamespace(control=SimpleNamespace(value=function)))

    def use_show_core(self):
        data = self.root / "SHOW" / "collections" / "test" / "_data"
        data.mkdir(parents=True)
        core = data / "test_metadata.csv"
        core.write_bytes(self.core.read_bytes())
        self.settings["core_metadata_csv"] = str(core)
        return data / "PRIVATE_test_metadata.csv"

    def test_analysis_retries_saved_inputs_after_volume_becomes_available(self):
        page = self.start_page(initially_unavailable=True)
        with patch.object(app, "shared_group_objects_by_source_directory",
                          wraps=app.shared_group_objects_by_source_directory) as group:
            self.execute(page, "function_1_list_files")
        self.assertEqual(1, group.call_count)
        self.assertEqual(self.inputs, group.call_args.args[4])
        self.assertEqual(2, len(group.call_args.args[0]))
        self.assertEqual("Function 1: Analyze Digital Assets", page.overlay[-1].title.value)

    def test_export_retries_saved_inputs_after_volume_becomes_available(self):
        page = self.start_page(initially_unavailable=True)
        self.execute(page, "function_2_export_csv")
        exports = list((self.root / ".DART-working-directory").glob("DART_export_*.csv"))
        self.assertEqual(1, len(exports))
        with exports[0].open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        parents = [row for row in rows if row["type"] == "compound"]
        children = [row for row in rows if row["type"] == "child"]
        self.assertEqual(2, len(parents))
        self.assertEqual(2, len(children))
        self.assertEqual({row["objectid"] for row in parents}, {row["parentid"] for row in children})

    def test_export_records_large_media_without_uploading_it(self):
        large = self.inputs / "first" / "first.jpg"
        with large.open("wb") as stream:
            stream.truncate(1_000_001)
        self.settings.update({"archive-only-file-threshold": 1,
                              "azure_blob_storage_path": "assets/objs/test",
                              "azure_connection_string": "AccountName=test"})
        page = self.start_page()
        client = Mock()
        client.get_container_client.return_value.exists.return_value = True
        client.get_blob_client.return_value.exists.return_value = False
        with patch.object(app, "init_azure_client", return_value=(True, client, "connected")), \
                patch.object(app, "upload_to_azure", return_value=(True, "uploaded")) as upload:
            self.execute(page, "function_2_export_csv")
        self.assertEqual(["second.jpg"], [Path(call.args[1]).name for call in upload.call_args_list])
        manifest = self.root / ".DART-working-directory" / dart_archive.MANIFEST_NAME
        record = json.loads(manifest.read_text())[0]
        self.assertEqual((str(large), 1_000_001), (record["original_path"], record["file_size_bytes"]))
        export = next((self.root / ".DART-working-directory").glob("DART_export_*.csv"))
        with export.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        row = next(row for row in rows if row["original_file_name"] == "first.jpg")
        self.assertEqual(record["objectid"], row["objectid"])
        self.assertEqual("record", row["display_template"])

    def test_private_compound_children_are_separate_and_never_uploaded(self):
        private_csv = self.use_show_core()
        public_core = Path(self.settings["core_metadata_csv"])
        core_before = public_core.read_bytes()
        first = self.inputs / "first" / "PRIVATE-form.pdf"
        second = self.inputs / "first" / "RESTRICTED-note.docx"
        first.write_bytes(b"private document")
        second.write_bytes(b"private document")
        private_only = self.inputs / "private-only"
        private_only.mkdir()
        (private_only / "PRIVATE-other.pdf").write_bytes(b"private")
        self.settings.update({
            "private_file_prefixes": "PRIVATE-;RESTRICTED-",
            "azure_blob_storage_path": "assets/objs/test",
            "azure_connection_string": "AccountName=test",
        })
        client = Mock()
        client.get_container_client.return_value.exists.return_value = True
        client.get_blob_client.return_value.exists.return_value = False
        page = self.start_page()
        with patch.object(app, "init_azure_client", return_value=(True, client, "connected")), \
                patch.object(app, "upload_to_azure", return_value=(True, "uploaded")) as upload:
            self.execute(page, "function_2_export_csv")
        self.assertEqual({"first.jpg", "second.jpg"}, {Path(call.args[1]).name for call in upload.call_args_list})
        with private_csv.open(newline="") as stream:
            private_rows = list(csv.DictReader(stream))
        self.assertEqual(core_before, public_core.read_bytes())
        self.assertEqual({"PRIVATE-form.pdf", "RESTRICTED-note.docx", "PRIVATE-other.pdf"},
                         {row["original_file_name"] for row in private_rows})
        self.assertEqual(3, len({row["objectid"] for row in private_rows}))
        self.assertTrue(all(row["objectid"] and row["parentid"] for row in private_rows))
        public_csv = next((self.root / ".DART-working-directory").glob("DART_export_*.csv"))
        with public_csv.open(newline="") as stream:
            public_rows = list(csv.DictReader(stream))
        self.assertTrue(all("PRIVATE-" not in str(row) and "RESTRICTED-" not in str(row)
                            for row in public_rows))
        parent_ids = {row["objectid"] for row in public_rows if row["type"] == "compound"}
        self.assertEqual(2, len(parent_ids))
        private_form = next(row for row in private_rows if row["original_file_name"] == first.name)
        self.assertIn(private_form["parentid"], parent_ids)
        manifest = self.root / ".DART-working-directory" / dart_archive.MANIFEST_NAME
        self.assertEqual(3, len(json.loads(manifest.read_text())))

        for path in (first, second, private_only / "PRIVATE-other.pdf"):
            path.unlink()
        previous = private_csv.read_bytes()
        self.settings["azure_connection_string"] = ""
        self.execute(page, "function_2_export_csv")
        self.assertEqual(previous, private_csv.read_bytes())

    def test_private_csv_invalid_destination_stops_before_upload(self):
        self.settings.update({
            "private_file_prefixes": "PRIVATE-",
            "azure_blob_storage_path": "assets/objs/test",
            "azure_connection_string": "AccountName=test",
        })
        page = self.start_page()
        with patch.object(app, "init_azure_client") as azure:
            self.execute(page, "function_2_export_csv")
        azure.assert_not_called()
        self.assertFalse((self.root / ".DART-working-directory").exists())

    def test_ohm_private_transcript_and_image_are_not_public(self):
        directory = self.inputs / "OHM-data" / "Person_dg_123"
        directory.mkdir(parents=True)
        (directory / "dg_123.mp3").write_bytes(b"audio")
        (directory / "dg_123.csv").write_text("start,end,text\n0,1,private\n")
        (directory / "PRIVATE-image.jpg").write_bytes(b"private")
        private_csv = self.use_show_core()
        self.settings.update({"process_OHM_data": True, "private_file_prefixes": "dg_123.csv;PRIVATE-"})
        page = self.start_page()
        self.execute(page, "function_2_export_csv")
        export = next((self.root / ".DART-working-directory").glob("DART_export_*.csv"))
        with export.open(newline="") as stream:
            public_rows = list(csv.DictReader(stream))
        self.assertEqual(1, len(public_rows))
        self.assertEqual(("test_dg_123", "record", ""), (
            public_rows[0]["objectid"], public_rows[0]["display_template"], public_rows[0]["object_transcript"]))
        with private_csv.open(newline="") as stream:
            private_rows = list(csv.DictReader(stream))
        self.assertEqual({"dg_123.csv", "PRIVATE-image.jpg"},
                         {row["original_file_name"] for row in private_rows})
        self.assertEqual({"test_dg_123"}, {row["parentid"] for row in private_rows})
        self.assertEqual(2, len({row["objectid"] for row in private_rows}))
        self.assertFalse((self.root / "_data" / "transcripts" / "test_dg_123.csv").exists())

    def test_derivatives_reject_old_export_containing_private_names(self):
        work = self.root / ".DART-working-directory"
        work.mkdir()
        (work / "DART_export_20200101_000000.csv").write_text(
            "objectid,original_file_name,filepath\nid,_PRIVATE-file.jpg,/missing\n"
        )
        self.settings.update({"private_file_prefixes": "PRIVATE-",
                              "azure_blob_storage_path": "assets/objs/test",
                              "azure_connection_string": "AccountName=test"})
        page = self.start_page()
        with patch.object(app, "init_azure_client", return_value=(True, Mock(), "connected")), \
                patch.object(app, "upload_to_azure") as upload:
            self.execute(page, "function_3_generate_derivatives")
        upload.assert_not_called()
        self.assertFalse((work / "temp_derivatives").exists())

    def test_ungrouped_private_file_fails_without_writing_export(self):
        (self.inputs / "PRIVATE-file.pdf").write_bytes(b"private")
        self.use_show_core()
        self.settings["private_file_prefixes"] = "PRIVATE-"
        page = self.start_page()
        self.execute(page, "function_2_export_csv")
        self.assertFalse(list((self.root / ".DART-working-directory").glob("DART_export_*.csv")))

    def test_merge_blocks_existing_private_records(self):
        self.core.write_text("objectid,original_file_name,parentid,title,type,filepath\n"
                             "id,_PRIVATE-file.jpg,,,,\n")
        work = self.root / ".DART-working-directory"
        work.mkdir()
        (work / "DART_export_20200101_000000.csv").write_text(
            "objectid,original_file_name,parentid,title,type,filepath\nid,public.jpg,,,,\n"
        )
        self.settings["private_file_prefixes"] = "PRIVATE-"
        page = self.start_page()
        with patch.object(app, "compare_metadata_rows") as compare:
            self.execute(page, "function_4_compare_merge")
            button = next(action for action in page.overlay[-1].actions if action.text == "Use Newest")
            button.on_click(None)
        compare.assert_not_called()
        self.assertIn("_PRIVATE-file.jpg", self.core.read_text())

    def test_private_csv_write_failure_does_not_publish_export(self):
        (self.inputs / "first" / "PRIVATE-file.pdf").write_bytes(b"private")
        self.use_show_core()
        self.settings["private_file_prefixes"] = "PRIVATE-"
        page = self.start_page()
        with patch.object(dart_archive, "write_private_csv", side_effect=OSError("read-only")):
            self.execute(page, "function_2_export_csv")
        self.assertFalse(list((self.root / ".DART-working-directory").glob("DART_export_*.csv")))

    def test_headless_settings_are_disabled_and_local_inputs_remain_usable(self):
        self.settings.update({"headless_host": "user@example.test",
                              "headless_project_dir": "/data/dart/data/projects/test"})
        page = self.start_page()
        toggle = next(control for control in self.walk(page.controls)
                      if isinstance(control, app.ft.IconButton)
                      and control.tooltip == "Expand/Collapse app settings section")
        toggle.on_click(None)
        controls = list(self.walk(page.controls))
        fields = [control for control in controls if isinstance(control, app.ft.TextField)]
        self.assertFalse(any(field.label == "Private Metadata CSV" for field in fields))
        for label in ("Headless Host", "Headless Project Directory"):
            field = next(field for field in fields if field.label == label)
            self.assertTrue(field.disabled)
        inputs = next(field for field in fields if field.label == "Inputs Folder")
        self.assertFalse(inputs.disabled)

    def test_missing_inputs_reports_configured_path_not_missing_selection(self):
        page = self.start_page()
        unavailable = self.root / "not-mounted"
        field = next(control for control in self.walk(page.controls)
                     if isinstance(control, app.ft.TextField) and control.label == "Inputs Folder")
        field.value = str(unavailable)
        for function in ("function_1_list_files", "function_2_export_csv"):
            with self.subTest(function=function):
                self.execute(page, function)
                texts = [control.value for control in self.walk(page.controls)
                         if isinstance(control, app.ft.Text)]
                self.assertIn(f"Error: Inputs Folder is unavailable or not a directory: {unavailable}", texts)

    def test_selected_file_export_does_not_require_inputs_folder(self):
        preferences = app.PersistentStorage()
        preferences.set_ui_state("last_input_dir", "")
        preferences.set_ui_state("last_file", str(self.inputs / "first" / "first.jpg"))
        self.settings["group_by_source_directory"] = False
        self.settings["group_compound_objects"] = False
        page = self.start_page()
        self.execute(page, "function_2_export_csv")
        export = next((self.root / ".DART-working-directory").glob("DART_export_*.csv"))
        with export.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(["first.jpg"], [row["original_file_name"] for row in rows])

    def test_non_directory_and_access_errors_are_reported(self):
        page = self.start_page()
        field = next(control for control in self.walk(page.controls)
                     if isinstance(control, app.ft.TextField) and control.label == "Inputs Folder")
        field.value = str(self.core)
        self.execute(page, "function_1_list_files")
        texts = [control.value for control in self.walk(page.controls)
                 if isinstance(control, app.ft.Text)]
        self.assertIn(f"Error: Inputs Folder is unavailable or not a directory: {self.core}", texts)
        field.value = str(self.inputs)
        original_is_dir = Path.is_dir

        def is_dir(path):
            if path == self.inputs:
                raise PermissionError("Access denied")
            return original_is_dir(path)

        with patch.object(Path, "is_dir", is_dir):
            self.execute(page, "function_1_list_files")
        texts = [control.value for control in self.walk(page.controls)
                 if isinstance(control, app.ft.Text)]
        self.assertIn(f"Error: Cannot access Inputs Folder {self.inputs}: Access denied", texts)

    def test_function_execution_rejects_overlap_and_reenables_selector_after_completion(self):
        page = self.start_page()
        group_objects = app.shared_group_objects_by_source_directory
        selector = next(control for control in self.walk(page.controls)
                        if isinstance(control, app.ft.Dropdown)
                        and control.label == "Select Function to Execute")

        def reenter(*args, **kwargs):
            self.assertTrue(selector.disabled)
            self.execute(page, "function_9_system_info")
            self.assertFalse(any(isinstance(control, app.ft.AlertDialog)
                                 and control.title.value == "Function 9: System Info"
                                 for control in page.overlay))
            texts = [control.value for control in self.walk(page.controls)
                     if isinstance(control, app.ft.Text)]
            self.assertIn(
                "Error: A workflow function is still running. Wait for it to finish before starting another.",
                texts,
            )
            return group_objects(*args, **kwargs)

        with patch.object(app, "shared_group_objects_by_source_directory", side_effect=reenter):
            self.execute(page, "function_1_list_files")
        self.assertFalse(selector.disabled)
        self.assertEqual("", selector.value)
        self.execute(page, "function_9_system_info")
        self.assertEqual("Function 9: System Info", page.overlay[-1].title.value)

    def test_function_failure_releases_execution_guard(self):
        page = self.start_page()
        with patch.object(app, "shared_group_objects_by_source_directory",
                          side_effect=RuntimeError("Test failure")):
            with self.assertRaisesRegex(RuntimeError, "Test failure"):
                self.execute(page, "function_1_list_files")
        self.execute(page, "function_9_system_info")
        self.assertEqual("Function 9: System Info", page.overlay[-1].title.value)


class DerivativeExportSelectionTests(unittest.TestCase):
    def test_newer_local_export_beats_old_handoff_and_outputs_are_excluded(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            files = [
                root / "DART_export_handoff_old.csv",
                root / "DART_export_20261105_160000.csv",
                root / "DART_export_with_gems_20261105_160100.csv",
                root / "DART_export_with_derivatives_20261105_160200.csv",
            ]
            for index, path in enumerate(files):
                path.write_text("original_file_name\n")
                os.utime(path, ns=(1000000000 + index, 1000000000 + index))
            self.assertEqual([files[1], files[0]], derivative_source_exports(root))
            os.utime(files[0], ns=(2000000000, 2000000000))
            self.assertEqual([files[0], files[1]], derivative_source_exports(root))

    def test_no_original_exports_returns_empty(self):
        with tempfile.TemporaryDirectory() as name:
            self.assertEqual([], derivative_source_exports(Path(name)))


if __name__ == "__main__":
    unittest.main()
