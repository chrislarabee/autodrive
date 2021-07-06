from autodrive.formatting import _cell as cell
from autodrive.interfaces import TwoDRange, Color


def test_add_alternating_row_background():
    result = cell.add_alternating_row_background(
        TwoDRange(0, 1, 5, 0, 10, base0_idxs=True), Color(0.2, 0.3)
    )
    assert result == {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [
                    {
                        "sheetId": 0,
                        "startRowIndex": 1,
                        "endRowIndex": 5,
                        "startColumnIndex": 0,
                        "endColumnIndex": 10,
                    }
                ],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": "=MOD(ROW(), 2)"}],
                    },
                    "format": {
                        "backgroundColor": {
                            "red": 0.2,
                            "green": 0.3,
                            "blue": 0,
                            "alpha": 1,
                        }
                    },
                },
            },
            "index": 1,
        }
    }
