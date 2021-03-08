from datetime import datetime as dt

import pytest


@pytest.mark.skip
class TestSheetsAPI:
    def test_batch_update(self, sheets_api):
        testing_tools.check_sheets_api_skip(sheets_api)

        sheet = f"data_genius_test_sheet {dt.now()}"
        s_id = sheets_api.create_object(sheet, "sheet")
        testing_tools.created_ids.insert(0, s_id)
        values = [["a", "b", "c"], ["1", "2", "3"], ["4", "5", "6"]]
        result = sheets_api.write_values(s_id, values)
        assert result == (3, 3)
        fmt = sheets_api.format_sheet(s_id).insert_rows(2)
        sheets_api.batch_update(s_id, fmt.requests)
        rows = sheets_api.get_sheet_values(s_id)
        expected = [[], [], *values]
        assert rows == expected
