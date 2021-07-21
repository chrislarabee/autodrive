from autodrive.formatting import _cell as cell
from autodrive.interfaces import FullRange, Color


def test_add_alternating_row_background():
    result = cell.add_alternating_row_background(
        0,
        FullRange(start_row=1, end_row=4, start_col=0, end_col=9, base0_idxs=True),
        Color(0.2, 0.3),
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
