from autodrive.dtypes import BorderDashed, BorderLeft, BorderRight
from autodrive.formatting import _cell as cell
from autodrive.interfaces import FullRange, Color, BorderFormat


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


def test_set_background_color():
    result = cell.set_background_color(0, FullRange("B5:D10"), Color(0.4, 0.7, 0.3))
    assert result == {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startRowIndex": 4,
                "endRowIndex": 10,
                "startColumnIndex": 1,
                "endColumnIndex": 4,
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.4,
                        "blue": 0.3,
                        "green": 0.7,
                        "alpha": 1.0,
                    }
                }
            },
            "fields": "userEnteredFormat",
        }
    }


def test_set_border_format():
    result = cell.set_border_format(
        0,
        FullRange("B5:D10"),
        BorderFormat(BorderLeft, Color(0, 1.0, 0)),
        BorderFormat(BorderRight, style=BorderDashed),
    )
    assert result == {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startRowIndex": 4,
                "endRowIndex": 10,
                "startColumnIndex": 1,
                "endColumnIndex": 4,
            },
            "cell": {
                "userEnteredFormat": {
                    "borders": {
                        "left": {
                            "color": {
                                "red": 0.0,
                                "green": 1.0,
                                "blue": 0.0,
                                "alpha": 1.0,
                            },
                            "style": "SOLID",
                        },
                        "right": {
                            "color": {
                                "red": 0.0,
                                "green": 0.0,
                                "blue": 0.0,
                                "alpha": 1.0,
                            },
                            "style": "DASHED",
                        },
                    }
                }
            },
            "fields": "userEnteredFormat",
        }
    }
