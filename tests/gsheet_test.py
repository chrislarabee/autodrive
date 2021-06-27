import pytest

from autodrive.gsheet import GSheet, Tab
from autodrive.connection import SheetsConnection


class TestGSheet:
    def test_that_it_acts_like_an_iterable(self):
        gsheet = GSheet(
            "test",
            tabs=[Tab("test", "Sheet1", 0, 0), Tab("test", "Sheet2", 1, 1)],
            autoconnect=False,
        )
        assert len(gsheet) == 2
        assert len(gsheet.keys()) == 2
        assert len(gsheet.values()) == 2
        assert gsheet["Sheet1"]
        assert gsheet[0]

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

    @pytest.mark.skip
    def test_that_it_can_add_tabs_requests(self, sheets_conn: SheetsConnection):
        expected = [
            {"addSheet": {"properties": {"title": "new_sheet"}}},
            {"addSheet": {"properties": {"title": "nuevo_sheet", "index": 3}}},
        ]
        gsheet = GSheet("test", sheets_conn=sheets_conn, autoconnect=False)
        gsheet.add_tab("new_sheet").add_tab("nuevo_sheet", 3)
        assert gsheet.requests == expected
