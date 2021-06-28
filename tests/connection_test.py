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

        # def test_create_sheet_and_add_tab_to_it(self, drive_conn):
        #     sheet = f"autodrive_test_sheet {dt.now()}"
        #     s_id = drive_conn.create_object(sheet, "sheet")
        #     testing_tools.CREATED_IDS.insert(0, s_id)
        #     f = drive_conn.find_object(sheet, "sheet")
        #     assert len(f) > 0
        #     assert f[0].get("name") == sheet
        #     md = drive_conn.sheets.get_tab_metadata(s_id)
        #     assert md["row_limit"] == 0
        #     assert md["col_limit"] == 0
        #     # Add a tab:
        #     result = drive_conn.sheets.add_tab(s_id)
        #     assert result == ("Sheet2", 1)
        #     # Add a tab with specific title:
        #     result = drive_conn.sheets.add_tab(s_id, title="test title")
        #     assert result == ("test title", 2)

    # class TestWritingAndReadingSheetValues:
    #     def test_write_and_read_values_to_sheet(self, api):
    #         # Create a sheet to add values to:
    #         sheet = f"autodrive_test_sheet {dt.now()}"
    #         s_id = api.create_object(sheet, "sheet")
    #         testing_tools.CREATED_IDS.insert(0, s_id)
    #         result = api.sheets.write_values(
    #             s_id, [["a", "b", "c"], [1, 2, 3], [4, 5, 6]]
    #         )
    #         assert result == (3, 3)
    #         expected = [["a", "b", "c"], ["1", "2", "3"], ["4", "5", "6"]]
    #         values = api.sheets.get_values(s_id)
    #         assert values == expected
    #         # Add values that don't start at A1:
    #         result = api.sheets.write_values(s_id, [[7, 8]], start_cell="C4")
    #         assert result == (1, 2)
    #         expected = [
    #             ["a", "b", "c"],
    #             ["1", "2", "3"],
    #             ["4", "5", "6"],
    #             ["", "", "7", "8"],
    #         ]
    #         values = api.sheets.get_values(s_id)
    #         assert values == expected
    #         # Read only value range:
    #         expected = [["b", "c"], ["2", "3"], ["5", "6"]]
    #         values = api.sheets.get_values(s_id, cell_range=("B1", "C3"))
    #         assert values == expected
