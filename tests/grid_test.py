import pytest

from autodrive.formatting import grid


def test_auto_column_width():
    result = grid.auto_column_width(0, 0, 5)
    assert result == {
        "autoResizeDimensions": {
            "dimensions": {
                "sheetId": 0,
                "dimension": "COLUMNS",
                "startIndex": 0,
                "endIndex": 5,
            }
        }
    }


def test_append_rows():
    result = grid.append_rows(0, 5)
    assert result == {
        "appendDimension": {"sheetId": 0, "dimension": "ROWS", "length": 5}
    }


def test_insert_rows():
    result = grid.insert_rows(0, 3, 2)
    assert result == {
        "insertDimension": {
            "range": {
                "sheetId": 0,
                "dimension": "ROWS",
                "startIndex": 2,
                "endIndex": 5,
            },
            "inheritFromBefore": False,
        }
    }


def test_delete_rows():
    result = grid.delete_rows(0, 5, 10)
    assert result == {
        "deleteDimension": {
            "range": {
                "sheetId": 0,
                "dimension": "ROWS",
                "startIndex": 5,
                "endIndex": 10,
            }
        }
    }


def test_freeze():
    result = grid.freeze(0, rows=1)
    assert result == {
        "updateSheetProperties": {
            "properties": {
                "sheetId": 0,
                "gridProperties": {"frozenRowCount": 1},
            },
            "fields": "gridProperties(frozenRowCount, frozenColumnCount)",
        }
    }
    result = grid.freeze(0, rows=2, columns=4)
    assert result == {
        "updateSheetProperties": {
            "properties": {
                "sheetId": 0,
                "gridProperties": {"frozenRowCount": 2, "frozenColumnCount": 4},
            },
            "fields": "gridProperties(frozenRowCount, frozenColumnCount)",
        }
    }
    with pytest.raises(ValueError, match="One of rows or columns must not be None"):
        # Set to ignore because this is properly flagged as an error.
        result = grid.freeze(0)  # type: ignore
