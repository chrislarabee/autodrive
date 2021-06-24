from autodrive.formatting import text
from autodrive.interfaces import TwoDRange, TextFormat, AccountingFormat


def test_apply_format():
    result = text.apply_format(TwoDRange(0, 0, 4), TextFormat(font_size=12, bold=True))
    assert result == {
        "repeatCell": {
            "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 4},
            "cell": {
                "userEnteredFormat": {"textFormat": {"fontSize": 12, "bold": True}}
            },
            "fields": "userEnteredFormat(textFormat)",
        }
    }
    result = text.apply_format(TwoDRange(0, 0, 4), AccountingFormat)
    assert result == {
        "repeatCell": {
            "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 4},
            "cell": {
                "userEnteredFormat": {
                    "numberFormat": {
                        "type": "NUMBER",
                        "pattern": AccountingFormat.pattern,
                    }
                }
            },
            "fields": "userEnteredFormat(numberFormat)",
        }
    }


# @pytest.mark.skip
# class TestSheetsAPI:
#     def test_batch_update(self, sheets_api):
#         testing_tools.check_sheets_api_skip(sheets_api)

#         sheet = f"data_genius_test_sheet {dt.now()}"
#         s_id = sheets_api.create_object(sheet, "sheet")
#         testing_tools.created_ids.insert(0, s_id)
#         values = [["a", "b", "c"], ["1", "2", "3"], ["4", "5", "6"]]
#         result = sheets_api.write_values(s_id, values)
#         assert result == (3, 3)
#         fmt = sheets_api.format_sheet(s_id).insert_rows(2)
#         sheets_api.batch_update(s_id, fmt.requests)
#         rows = sheets_api.get_sheet_values(s_id)
#         expected = [[], [], *values]
#         assert rows == expected
