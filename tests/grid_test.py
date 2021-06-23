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
