from datetime import datetime as dt

from gsheet_api.api import GSheetsAPI
from . import testing_tools


class TestAPI:
    def test_connect(self):
        connections = GSheetsAPI().connect()
        assert len(connections) == 2

    class TestDrive:
        class TestCreateObject:
            def test_create_folder(self, api):
                folder = f"gsheet_api_test_folder {dt.now()}"
                f_id = api.drive.create_object(folder, "folder")
                testing_tools.CREATED_IDS.insert(0, f_id)
                f = api.drive.find_object(folder, "folder")
                assert len(f) > 0
                assert f[0].get("name") == folder

            def test_create_sheet(self, api):
                sheet = f"data_genius_test_sheet {dt.now()}"
                s_id = api.drive.create_object(sheet, "sheet")
                testing_tools.CREATED_IDS.insert(0, s_id)
                f = api.drive.find_object(sheet, "sheet")
                assert len(f) > 0
                assert f[0].get("name") == sheet
                md = api.sheets.get_sheet_metadata(s_id)
                assert md["row_limit"] == 0
                assert md["col_limit"] == 0
