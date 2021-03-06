from datetime import datetime as dt

import pandas as pd
import pytest


@pytest.mark.skip
def test_write_gsheet_and_from_gsheet(sheets_api):
    testing_tools.check_sheets_api_skip(sheets_api)

    sheet = f"data_genius_test_sheet {dt.now()}"
    df = pd.DataFrame([dict(a=1, b=2), dict(a=3, b=4)])
    sheet_id, shape = text.write_gsheet(sheet, df, s_api=sheets_api)
    testing_tools.created_ids.append(sheet_id)
    expected = pd.DataFrame([["a", "b"], ["1", "2"], ["3", "4"]])
    assert shape == (3, 2)
    read_df = text.from_gsheet(sheet + ".sheet", sheets_api)
    pd.testing.assert_frame_equal(read_df, expected)

    # Write to a new sheet:
    df = pd.DataFrame([dict(c=5, d=6), dict(c=7, d=8)])
    sheet_id2, shape = text.write_gsheet(
        sheet, df, sheet_title="test_sheet", s_api=sheets_api
    )
    assert sheet_id2 == sheet_id
    expected = pd.DataFrame([["c", "d"], ["5", "6"], ["7", "8"]])
    assert shape == (3, 2)
    read_df = text.from_gsheet(sheet + ".sheet", sheets_api, "test_sheet")
    pd.testing.assert_frame_equal(read_df, expected)

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
    def test_basics(self, sheets_api):
        testing_tools.check_sheets_api_skip(sheets_api)

        # Create a folder:
        folder = f"data_genius_test_folder {dt.now()}"
        f_id = sheets_api.create_object(folder, "folder")
        testing_tools.created_ids.append(f_id)
        f = sheets_api.find_object(folder, "folder")
        assert len(f) > 0
        assert f[0].get("name") == folder

        # Create a file:
        sheet = f"data_genius_test_sheet {dt.now()}"
        s_id = sheets_api.create_object(sheet, "sheet")
        testing_tools.created_ids.insert(0, s_id)
        f = sheets_api.find_object(sheet, "sheet")
        assert len(f) > 0
        assert f[0].get("name") == sheet
        md = sheets_api.get_sheet_metadata(s_id)
        assert md["row_limit"] == 0
        assert md["col_limit"] == 0

        # Add sheets to it:
        result = sheets_api.add_sheet(s_id)
        assert result == ("Sheet2", 1)

        result = sheets_api.add_sheet(s_id, title="test title")
        assert result == ("test title", 2)

        # Create a file IN the folder:
        sheet = f"data_genius_test_sheet_in_folder {dt.now()}"
        sf_id = sheets_api.create_object(sheet, "sheet", f_id)
        testing_tools.created_ids.insert(0, sf_id)
        f = sheets_api.find_object(sheet, "sheet")
        assert len(f) > 0
        assert f[0].get("name") == sheet
        assert f[0].get("parents")[0] == f_id

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


@pytest.mark.skip
class TestGSheetFormatting:
    def test_auto_column_width(self):
        f = text.GSheetFormatting("")
        f.auto_column_width(0, 5)
        assert f.requests == [
            dict(
                autoResizeDimensions=dict(
                    dimensions=dict(
                        sheetId=0, dimension="COLUMNS", startIndex=0, endIndex=5
                    )
                )
            )
        ]

    def test_append_rows(self):
        f = text.GSheetFormatting("")
        f.append_rows(5)
        assert f.requests == [
            dict(appendDimension=dict(sheetId=0, dimension="ROWS", length=5))
        ]

    def test_insert_rows(self):
        f = text.GSheetFormatting("")
        f.insert_rows(3, 2)
        assert f.requests == [
            dict(
                insertDimension=dict(
                    range=dict(sheetId=0, dimension="ROWS", startIndex=2, endIndex=5),
                    inheritFromBefore=False,
                )
            )
        ]

    def test_delete_rows(self):
        f = text.GSheetFormatting("")
        f.delete_rows(5, 10)
        assert f.requests == [
            dict(
                deleteDimension=dict(
                    range=dict(sheetId=0, dimension="ROWS", startIndex=5, endIndex=10)
                )
            )
        ]

    def test_apply_font(self):
        f = text.GSheetFormatting("")
        f.apply_font((0, 4), size=12, style="bold")
        assert f.requests == [
            dict(
                repeatCell=dict(
                    range=dict(sheetId=0, startRowIndex=0, endRowIndex=4),
                    cell=dict(
                        userEnteredFormat=dict(textFormat=dict(fontSize=12, bold=True))
                    ),
                    fields="userEnteredFormat(textFormat)",
                )
            )
        ]

    def test_apply_nbr_format(self):
        f = text.GSheetFormatting("")
        f.apply_nbr_format("accounting", (0, 4))
        assert f.requests == [
            dict(
                repeatCell=dict(
                    range=dict(sheetId=0, startRowIndex=0, endRowIndex=4),
                    cell=dict(
                        userEnteredFormat=dict(
                            numberFormat=dict(
                                type="NUMBER",
                                pattern="_($* #,##0.00_);_($* (#,##0.00);"
                                '_($* "-"??_);_(@_)',
                            )
                        )
                    ),
                    fields="userEnteredFormat.numberFormat",
                )
            )
        ]

    def test_freeze(self):
        f = text.GSheetFormatting("")
        f.freeze(1).freeze(2, 4)
        assert f.requests == [
            dict(
                updateSheetProperties=dict(
                    properties=dict(sheetId=0, gridProperties=dict(frozenRowCount=1)),
                    fields="gridProperties(frozenRowCount, frozenColumnCount)",
                ),
            ),
            dict(
                updateSheetProperties=dict(
                    properties=dict(
                        sheetId=0,
                        gridProperties=dict(frozenRowCount=2, frozenColumnCount=4),
                    ),
                    fields="gridProperties(frozenRowCount, frozenColumnCount)",
                )
            ),
        ]

    def test_alternate_row_background(self):
        f = text.GSheetFormatting("")
        f.alternate_row_background(0.2, 0.3, row_idxs=(1, 5), col_idxs=(0, 10))
        assert f.requests == [
            dict(
                addConditionalFormatRule=dict(
                    rule=dict(
                        ranges=[
                            dict(
                                sheetId=0,
                                startRowIndex=1,
                                endRowIndex=5,
                                startColumnIndex=0,
                                endColumnIndex=10,
                            )
                        ],
                        booleanRule=dict(
                            condition=dict(
                                type="CUSTOM_FORMULA",
                                values=[dict(userEnteredValue="=MOD(ROW(), 2)")],
                            ),
                            format=dict(
                                backgroundColor=dict(red=0.2, green=0.3, blue=0)
                            ),
                        ),
                    ),
                    index=0,
                )
            )
        ]

    def test_build_repeat_cell_dict(self):
        assert text.GSheetFormatting._build_repeat_cell_dict(
            {"numberFormat": {"type": "x", "pattern": "y"}},
            row_idxs=(0, 5),
            col_idxs=(0, 2),
        ) == dict(
            range=dict(
                sheetId=0,
                startRowIndex=0,
                endRowIndex=5,
                startColumnIndex=0,
                endColumnIndex=2,
            ),
            cell=dict(userEnteredFormat=dict(numberFormat=dict(type="x", pattern="y"))),
        )

    def test_build_range_dict(self):
        assert text.GSheetFormatting._build_range_dict(0, (0, 4)) == dict(
            sheetId=0, startRowIndex=0, endRowIndex=4
        )

        with pytest.raises(ValueError, match="Must pass one or both of"):
            text.GSheetFormatting._build_range_dict()

    def test_build_color_dict(self):
        assert text.GSheetFormatting._build_color_dict(0, 1) == dict(
            red=0, green=1, blue=0
        )
        assert text.GSheetFormatting._build_color_dict(0.2, 0.4, 0.6, 0.8) == dict(
            red=0.2, green=0.4, blue=0.6
        )
