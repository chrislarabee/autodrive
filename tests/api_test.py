from datetime import datetime as dt

from gsheet_api.api import GSheetsAPI
from . import testing_tools


class TestAPI:
    def test_connect(self):
        connections = GSheetsAPI().connect()
        assert len(connections) == 2

    class TestObjectCreationAndMetadataChanges:
        def test_create_folder_and_add_sheet_to_it(self, api):
            folder = f"gsheet_api_test_folder {dt.now()}"
            f_id = api.drive.create_object(folder, "folder")
            testing_tools.CREATED_IDS.insert(0, f_id)
            f = api.drive.find_object(folder, "folder")
            assert len(f) > 0
            assert f[0].get("name") == folder
            # Add a sheet
            sheet = f"gsheet_api_test_sheet_in_folder {dt.now()}"
            sf_id = api.drive.create_object(sheet, "sheet", f_id)
            testing_tools.CREATED_IDS.insert(0, sf_id)
            f = api.drive.find_object(sheet, "sheet")
            assert len(f) > 0
            assert f[0].get("name") == sheet
            assert f[0].get("parents")[0] == f_id

        def test_create_sheetand_add_tab_to_it(self, api):
            sheet = f"gsheet_api_test_sheet {dt.now()}"
            s_id = api.drive.create_object(sheet, "sheet")
            testing_tools.CREATED_IDS.insert(0, s_id)
            f = api.drive.find_object(sheet, "sheet")
            assert len(f) > 0
            assert f[0].get("name") == sheet
            md = api.sheets.get_tab_metadata(s_id)
            assert md["row_limit"] == 0
            assert md["col_limit"] == 0
            # Add a tab:
            result = api.sheets.add_tab(s_id)
            assert result == ("Sheet2", 1)
            # Add a tab with specific title:
            result = api.sheets.add_sheet(s_id, title="test title")
            assert result == ("test title", 2)

