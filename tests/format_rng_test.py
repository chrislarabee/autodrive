import pytest

from autodrive.range import Range
from autodrive.tab import Tab
from autodrive.interfaces import Color, TextFormat, TwoDRange
from autodrive.gsheet import GSheet
from autodrive.connection import SheetsConnection


class TestRangeFormatting:
    @pytest.fixture(scope="session")
    def test_tab(self, sheets_conn: SheetsConnection, test_gsheet: GSheet):
        t = Tab(
            test_gsheet.gsheet_id,
            tab_title="rng_format",
            tab_id=10,
            tab_idx=2,
            column_count=10,
            row_count=500,
            sheets_conn=sheets_conn,
        )
        t.create()
        return t

    @pytest.mark.connection
    def test_formatting_applications(
        self, test_tab: Tab, sheets_conn: SheetsConnection
    ):
        rng = Range(
            TwoDRange(test_tab.tab_id, range_str="C3"),
            test_tab.gsheet_id,
            tab_title="rng_format",
            sheets_conn=sheets_conn,
        )
        rng.format_cell.add_alternating_row_background(Color(1.0, 0.5))
        rng.format_text.apply_format(TextFormat(font_size=14, bold=True))
        rng.commit()
        rng.get_data()
        cell1 = rng.formats[0][0]
        assert cell1["backgroundColor"]["red"] == 1
        assert cell1["backgroundColor"]["green"] == 0.49803922
        assert cell1["textFormat"]["bold"]
        assert cell1["textFormat"]["fontSize"] == 14
