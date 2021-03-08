from datetime import datetime as dt

import pandas as pd
import pytest


@pytest.mark.skip
def test_write_gsheet_and_from_gsheet(sheets_api):
    # "Append" to a new sheet:
    df = pd.DataFrame([dict(c=5, d=6), dict(c=7, d=8)])
    sheet_id2, shape = text.write_gsheet(
        sheet, df, sheet_title="test_sheet2", s_api=sheets_api, append=True
    )
    assert sheet_id2 == sheet_id
    expected = pd.DataFrame([["c", "d"], ["5", "6"], ["7", "8"]])
    assert shape == (3, 2)
    read_df = text.from_gsheet(sheet + ".sheet", sheets_api, "test_sheet2")
    pd.testing.assert_frame_equal(read_df, expected)

    # Append to the sheet:
    df = pd.DataFrame([dict(c=9, d=10), dict(c=11, d=12)])
    text.write_gsheet(
        sheet, df, sheet_title="test_sheet", s_api=sheets_api, append=True
    )
    expected = expected.append(pd.DataFrame([["9", "10"], ["11", "12"]])).reset_index(
        drop=True
    )
    read_df = text.from_gsheet(sheet + ".sheet", sheets_api, "test_sheet")
    pd.testing.assert_frame_equal(read_df, expected)


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
