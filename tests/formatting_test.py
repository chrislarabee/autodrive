import pytest

from gsheet_api.formatting import GSheetFormatting


class TestGSheetFormatting:
    def test_auto_column_width(self):
        f = GSheetFormatting("")
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
        f = GSheetFormatting("")
        f.append_rows(5)
        assert f.requests == [
            dict(appendDimension=dict(sheetId=0, dimension="ROWS", length=5))
        ]

    def test_insert_rows(self):
        f = GSheetFormatting("")
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
        f = GSheetFormatting("")
        f.delete_rows(5, 10)
        assert f.requests == [
            dict(
                deleteDimension=dict(
                    range=dict(sheetId=0, dimension="ROWS", startIndex=5, endIndex=10)
                )
            )
        ]

    def test_apply_font(self):
        f = GSheetFormatting("")
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
        f = GSheetFormatting("")
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
        f = GSheetFormatting("")
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
        f = GSheetFormatting("")
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
        assert GSheetFormatting._build_repeat_cell_dict(
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
        assert GSheetFormatting._build_range_dict(0, (0, 4)) == dict(
            sheetId=0, startRowIndex=0, endRowIndex=4
        )

        with pytest.raises(ValueError, match="Must pass one or both of"):
            GSheetFormatting._build_range_dict()

    def test_build_color_dict(self):
        assert GSheetFormatting._build_color_dict(0, 1) == dict(red=0, green=1, blue=0)
        assert GSheetFormatting._build_color_dict(0.2, 0.4, 0.6, 0.8) == dict(
            red=0.2, green=0.4, blue=0.6
        )
