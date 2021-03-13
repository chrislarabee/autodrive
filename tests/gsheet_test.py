import gsheet_api.gsheet as gs


class TestTab:
    class TestParseRowData:
        def test_that_it_can_parse_mixed_empty_and_populated_cells(self):
            raw = [
                {'values': [{}, {}, {'userEnteredValue': {'stringValue': 'test'}}]},
                {'values': [{}, {'userEnteredValue': {'numberValue': 1}}, {}]},
                {'values': [{'userEnteredValue': {'stringValue': '=A1+A2'}}]},
            ]
            expected = [[None, None, "test"], [None, 1, None], ["=A1+A2"]]
            assert gs.Tab.parse_row_data(raw) == expected