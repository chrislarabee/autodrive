from autodrive.formatting import _text as text
from autodrive.interfaces import FullRange, TextFormat, AccountingFormat


def test_apply_format_works_with_text_format():
    result = text.apply_format(
        0,
        FullRange(start_row=0, end_row=3, base0_idxs=True),
        TextFormat(font_size=12, bold=True),
    )
    assert result == {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startRowIndex": 0,
                "endRowIndex": 4,
                "startColumnIndex": 0,
                "endColumnIndex": 1,
            },
            "cell": {
                "userEnteredFormat": {"textFormat": {"fontSize": 12, "bold": True}}
            },
            "fields": "userEnteredFormat(textFormat)",
        }
    }


def test_apply_format_works_with_number_formats():
    result = text.apply_format(
        0, FullRange(start_row=0, end_row=3, base0_idxs=True), AccountingFormat
    )
    assert result == {
        "repeatCell": {
            "range": {
                "sheetId": 0,
                "startRowIndex": 0,
                "endRowIndex": 4,
                "startColumnIndex": 0,
                "endColumnIndex": 1,
            },
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
