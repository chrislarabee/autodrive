from typing import List, Dict, Any
import string

from autodrive.dtypes import FormattedVal, UserEnteredVal, EffectiveVal
from autodrive._view import GSheetView
from autodrive.interfaces import FullRange
from autodrive.range import Range
from .samples.data import ExampleView


class TestGSheetView:
    def test_that_it_can_parse_properties(self):
        expected = (
            "scratch",
            [
                {"sheetId": 0, "title": "Sheet1", "index": 0},
                {"sheetId": 1, "title": "Sheet2", "index": 1},
            ],
        )
        raw = {
            "properties": {"title": "scratch"},
            "sheets": [
                {"properties": {"sheetId": 0, "title": "Sheet1", "index": 0}},
                {"properties": {"sheetId": 1, "title": "Sheet2", "index": 1}},
            ],
        }
        assert GSheetView._parse_properties(raw) == expected

    def test_that_it_can_parse_row_data(self):
        fmt1 = {"col_rangeAlignment": "left"}
        value1 = {
            "formattedValue": "test",
            "userEnteredValue": {"stringValue": "test"},
            "effectiveValue": {"stringValue": "test"},
            "effectiveFormat": fmt1,
        }
        fmt2 = {"textFormat": {"bold": True}}
        value2 = {
            "formattedValue": "1",
            "userEnteredValue": {"numberValue": "1"},
            "effectiveValue": {"numberValue": 1},
            "effectiveFormat": fmt2,
        }
        fmt3 = {"backGroundColor": {"red": 0.5, "green": 0, "blue": 0.5}}
        value3 = {
            "formattedValue": "3",
            "userEnteredValue": {"formulaValue": "=A1+A2"},
            "effectiveValue": {"numberValue": 3},
            "effectiveFormat": fmt3,
        }
        raw: List[Dict[str, List[Dict[str, Any]]]] = [
            dict(values=[{}, {}, value1]),
            dict(values=[{}, value2, {}]),
            dict(values=[value3]),
        ]
        expected_values = [[None, None, "test"], [None, 1, None], ["=A1+A2"]]
        expected_formats = [[{}, {}, fmt1], [{}, fmt2, {}], [fmt3]]
        values, formats = GSheetView._parse_row_data(raw, value_type=UserEnteredVal)
        assert values == expected_values
        assert formats == expected_formats
        expected_values = [[None, None, "test"], [None, 1, None], [3]]
        values, formats = GSheetView._parse_row_data(raw, value_type=EffectiveVal)
        assert values == expected_values
        expected_values = [[None, None, "test"], [None, "1", None], ["3"]]
        values, formats = GSheetView._parse_row_data(raw, value_type=FormattedVal)
        assert values == expected_values

    def test_that_it_can_gen_cell_write_value(self):
        assert GSheetView._gen_cell_write_value(1) == {
            "userEnteredValue": {"numberValue": 1}
        }
        assert GSheetView._gen_cell_write_value(1.123) == {
            "userEnteredValue": {"numberValue": 1.123}
        }
        assert GSheetView._gen_cell_write_value([1, 2, 3]) == {
            "userEnteredValue": {"stringValue": [1, 2, 3]}
        }
        assert GSheetView._gen_cell_write_value(True) == {
            "userEnteredValue": {"boolValue": True}
        }
        assert GSheetView._gen_cell_write_value("=A1+B2") == {
            "userEnteredValue": {"formulaValue": "=A1+B2"}
        }

    def test_that_it_can_create_write_values_requests(self):
        comp = ExampleView(gsheet_id="test")
        rng = Range(
            FullRange("Sheet1!A1:C3"),
            tab_title="",
            tab_id=0,
            gsheet_id="test",
            autoconnect=False,
        )
        data1: List[List[Any]] = [["a", "b", "c"], [1, 2, 3], [4, 5, 6]]
        comp._write_values(data1, 0, rng.range.to_dict())
        str_w_vals = [{"userEnteredValue": {"stringValue": v}} for v in data1[0]]
        int_w_vals = [
            [{"userEnteredValue": {"numberValue": v}} for v in row] for row in data1[1:]
        ]
        expected = [
            {
                "updateCells": {
                    "fields": "*",
                    "rows": [
                        {"values": str_w_vals},
                        *[{"values": int_vals} for int_vals in int_w_vals],
                    ],
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 0,
                        "endRowIndex": 3,
                        "startColumnIndex": 0,
                        "endColumnIndex": 3,
                    },
                }
            }
        ]
        assert comp.requests == expected
        comp._requests = []
        data2: List[Dict[str, int]] = [dict(a=1, b=2, c=3), dict(a=4, b=5, c=6)]
        comp._write_values(data2, 0, rng.range.to_dict())
        assert comp.requests == expected

    def test_that_it_can_gen_alpha_keys(self):
        assert GSheetView.gen_alpha_keys(5) == [*string.ascii_uppercase[:5]]
        expected = [*string.ascii_uppercase, "AA", "AB"]
        assert GSheetView.gen_alpha_keys(28) == expected
