from autodrive.dtypes import AlignCenter, AlignTop
from autodrive.formatting import _text as text
from autodrive.interfaces import FullRange, TextFormat, AccountingFormat


RNG = FullRange(start_row=0, end_row=3, base0_idxs=True)
RNG_DICT = {
    "sheetId": 0,
    "startRowIndex": 0,
    "endRowIndex": 4,
    "startColumnIndex": 0,
    "endColumnIndex": 1,
}


def test_apply_format_works_with_text_format():
    result = text.apply_format(0, RNG, TextFormat(font_size=12, bold=True))
    assert result == {
        "repeatCell": {
            "range": RNG_DICT,
            "cell": {
                "userEnteredFormat": {"textFormat": {"fontSize": 12, "bold": True}}
            },
            "fields": "userEnteredFormat(textFormat)",
        }
    }


def test_apply_format_works_with_number_formats():
    result = text.apply_format(0, RNG, AccountingFormat)
    assert result == {
        "repeatCell": {
            "range": RNG_DICT,
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


def test_set_text_alignment():
    result = text.set_text_alignment(0, RNG, AlignCenter, AlignTop)
    assert result == {
        "repeatCell": {
            "range": RNG_DICT,
            "cell": {
                "userEnteredFormat": {
                    "verticalAlignment": "TOP",
                    "horizontalAlignment": "CENTER",
                }
            },
            "fields": "*",
        }
    }
