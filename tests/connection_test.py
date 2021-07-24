from datetime import datetime as dt

import pytest

from autodrive.connection import DriveConnection
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
