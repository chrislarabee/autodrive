import autodrive.gsheet as gs


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
    def test_that_it_can_add_tabs_requests(self, sheets_conn):
        expected = [
            {"addSheet": {"properties": {"title": "new_sheet", "index": 0}}},
            {"addSheet": {"properties": {"title": "nuevo_sheet", "index": 3}}},
        ]
        gsheet = gs.GSheet("test", sheets_conn=sheets_conn)
        gsheet.add_tab("new_sheet").add_tab("nuevo_sheet", 3)
        assert gsheet.requests == expected
