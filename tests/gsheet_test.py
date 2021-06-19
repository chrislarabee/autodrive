import pytest

from autodrive.gsheet import GSheet, Component, Range


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


class TestRange:
    def test_that_it_can_parse_range_strings(self):
        assert Range._parse_range("Sheet1!A1:C5") == ("Sheet1", "A1", "C5")
        assert Range._parse_range("A1:C50") == (None, "A1", "C50")
        assert Range._parse_range("A1:A") == (None, "A1", "A")
        assert Range._parse_range("A1") == (None, "A1", None)
        with pytest.raises(ValueError, match="parb is not a valid range."):
            Range._parse_range("parb")


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
