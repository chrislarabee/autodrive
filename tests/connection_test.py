from datetime import datetime as dt
from pathlib import Path

import pytest

from autodrive.connection import DriveConnection, FileUpload
from . import testing_tools


@pytest.mark.connection
class TestDriveConnection:
    class TestObjectCreationAndMetadataChanges:
        def test_create_folder_and_add_sheet_to_it(self, drive_conn: DriveConnection):
            folder = f"autodrive_test_folder {dt.now()}"
            f_id = drive_conn.create_object(folder, "folder")
            testing_tools.CREATED_IDS.insert(0, f_id)
            f = drive_conn.find_object(folder, "folder")
            assert len(f) > 0
            assert f[0].get("name") == folder
            # Add a sheet
            sheet = f"autodrive_test_sheet_in_folder {dt.now()}"
            sf_id = drive_conn.create_object(sheet, "sheet", f_id)
            testing_tools.CREATED_IDS.insert(0, sf_id)
            f = drive_conn.find_object(sheet, "sheet")
            assert len(f) > 0
            assert f[0].get("name") == sheet
            assert f[0]["parents"][0] == f_id

        def test_upload_files(self, drive_conn: DriveConnection):
            samples = Path("tests/sample_files")
            fileA = samples.joinpath("textfileA.txt")
            fileB = samples.joinpath("textfileB.txt")
            fileC = samples.joinpath("textfileC.txt")
            f_id1 = drive_conn.create_object(
                f"autodrive_test_folder {dt.now()}", "folder"
            )
            f_id2 = drive_conn.create_object(
                f"autodrive_test_folder {dt.now()}", "folder"
            )
            testing_tools.CREATED_IDS.insert(0, f_id1)
            testing_tools.CREATED_IDS.insert(0, f_id2)
            result = drive_conn.upload_files(
                str(fileA),
                FileUpload(fileB, f_id1),
                FileUpload(str(fileC), f_id2, convert=True),
            )
            testing_tools.CREATED_IDS.insert(0, result[fileA.name])
            testing_tools.CREATED_IDS.insert(0, result[fileB.name])
            testing_tools.CREATED_IDS.insert(0, result[fileC.name])
            f = drive_conn.find_object(fileA.name, "file")
            assert len(f) > 0
            assert f[0].get("name") == fileA.name
            f = drive_conn.find_object(fileB.name, "file")
            assert len(f) > 0
            assert f[0].get("name") == fileB.name
            assert f[0].get("parents") == [f_id1]
            f = drive_conn.find_object(fileC.stem, "file")
            assert len(f) > 0
            assert f[0].get("name") == fileC.stem
            assert f[0].get("parents") == [f_id2]
