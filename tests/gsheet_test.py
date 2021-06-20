import string

import pytest

from autodrive.gsheet import GSheet, Component, Range, ParseRangeError


class TestComponent:
    def test_that_it_can_parse_row_data(self):
        value1 = {"formattedValue": "test", "userEnteredValue": {"stringValue": "test"}}
        value2 = {"formattedValue": 1, "userEnteredValue": {"numberValue": 1}}
        value3 = {"formattedValue": 3, "userEnteredValue": {"stringValue": "=A1+A2"}}
        raw = [
            dict(values=[{}, {}, value1]),
            dict(values=[{}, value2, {}]),
            dict(values=[value3]),
        ]
        expected = [[None, None, "test"], [None, 1, None], ["=A1+A2"]]
        assert Component._parse_row_data(raw, get_formatted=False) == expected
        expected = [[None, None, "test"], [None, 1, None], [3]]
        assert Component._parse_row_data(raw, get_formatted=True) == expected

    def test_that_it_can_gen_cell_write_value(self):
        assert Component._gen_cell_write_value(1) == {
            "userEnteredValue": {"numberValue": 1}
        }
        assert Component._gen_cell_write_value(1.123) == {
            "userEnteredValue": {"numberValue": 1.123}
        }
        assert Component._gen_cell_write_value([1, 2, 3]) == {
            "userEnteredValue": {"stringValue": [1, 2, 3]}
        }
        assert Component._gen_cell_write_value(True) == {
            "userEnteredValue": {"boolValue": True}
        }
        assert Component._gen_cell_write_value("=A1+B2") == {
            "userEnteredValue": {"formulaValue": "=A1+B2"}
        }

    def test_that_it_can_create_write_values_requests(self, testing_component):
        comp = testing_component()
        data = [["a", "b", "c"], [1, 2, 3], [4, 5, 6]]
        comp._write_values(data)
        str_w_vals = [{"userEnteredValue": {"stringValue": v}} for v in data[0]]
        int_w_vals = [
            [{"userEnteredValue": {"numberValue": v}} for v in row] for row in data[1:]
        ]
        assert comp.requests == [
            {
                "updateCells": {
                    "fields": "*",
                    "rows": [
                        {
                            "values": [
                                str_w_vals,
                                *int_w_vals,
                            ]
                        }
                    ],
                }
            }
        ]

    def test_that_it_can_gen_alpha_keys(self):
        assert Component.gen_alpha_keys(5) == [*string.ascii_uppercase[:5]]
        expected = [*string.ascii_uppercase, "AA", "AB"]
        assert Component.gen_alpha_keys(28) == expected


class TestRange:
    def test_that_it_can_parse_range_strings(self):
        assert Range._parse_range_str("Sheet1!A1:C5") == ("Sheet1", "A1", "C5")
        assert Range._parse_range_str("A1:C50") == (None, "A1", "C50")
        assert Range._parse_range_str("A1:A") == (None, "A1", "A")
        assert Range._parse_range_str("A1") == (None, "A1", None)
        with pytest.raises(ParseRangeError, match="parb is not a valid range."):
            Range._parse_range_str("parb")

    def test_that_it_can_parse_cell_strings(self):
        assert Range._parse_cell_str("A1") == ("A", "1")
        assert Range._parse_cell_str("A") == ("A", None)

    def test_that_it_can_convert_cell_str_to_coordinate(self):
        assert Range._convert_cell_str_to_coord("A5") == (0, 6)
        assert Range._convert_cell_str_to_coord("AA") == (26, None)
        assert Range._convert_cell_str_to_coord("BC127") == (54, 128)

    def test_that_it_can_construct_range_strings(self):
        assert Range._construct_range_str("Sheet1") == "Sheet1"
        assert Range._construct_range_str("Sheet1", (0, 5), (5, 10)) == "Sheet1!E1:J6"

    def test_that_it_can_convert_alpha_col_to_idx(self):
        assert Range._convert_alpha_col_to_idx("A") == 0
        assert Range._convert_alpha_col_to_idx("AA") == 26
        assert Range._convert_alpha_col_to_idx("AAA") == 702
        assert Range._convert_alpha_col_to_idx("BA") == 52
        assert Range._convert_alpha_col_to_idx("ZA") == 676


# class TestTab:
#     class TestParseRowData:
#         def test_that_it_can_parse_mixed_empty_and_populated_cells(self):
#             raw = [
#                 {'values': [{}, {}, {'userEnteredValue': {'stringValue': 'test'}}]},
#                 {'values': [{}, {'userEnteredValue': {'numberValue': 1}}, {}]},
#                 {'values': [{'userEnteredValue': {'stringValue': '=A1+A2'}}]},
#             ]
#             expected = [[None, None, "test"], [None, 1, None], ["=A1+A2"]]
#             assert gs.Tab.parse_row_data(raw) == expected


class TestGSheet:
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
        assert GSheet._parse_properties(raw) == expected

    def test_that_it_can_add_tabs_requests(self, sheets_conn):
        expected = [
            {"addSheet": {"properties": {"title": "new_sheet", "index": 0}}},
            {"addSheet": {"properties": {"title": "nuevo_sheet", "index": 3}}},
        ]
        gsheet = GSheet("test", sheets_conn=sheets_conn)
        gsheet._partial = False
        gsheet.add_tab("new_sheet").add_tab("nuevo_sheet", 3)
        assert gsheet.requests == expected
