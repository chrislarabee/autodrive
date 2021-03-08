from gsheet_api.sheets import Sheets


class TestSheets:
    def test_gen_last_cell(self):
        assert Sheets.gen_last_cell(dict(row_limit=5, col_limit=7)) == "G5"

    def test_parse_cell_range(self):
        assert Sheets._parse_cell_range(("A3", "C3")) == ("A3", "C3")
        assert Sheets._parse_cell_range(("C3", None)) == ("A1", "C3")
