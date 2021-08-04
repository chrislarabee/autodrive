from autodrive.dtypes import BorderSolidThick
import pytest

from autodrive.tab import Tab
from autodrive.interfaces import Color, TextFormat, FullRange
from autodrive.gsheet import GSheet
from autodrive.connection import SheetsConnection


class TestFormatting:
    @pytest.fixture(scope="session")
    def test_tab(self, sheets_conn: SheetsConnection, test_gsheet: GSheet):
        t = Tab(
            test_gsheet.gsheet_id,
            tab_title="test_formatting",
            tab_id=10,
            tab_idx=2,
            column_count=10,
            row_count=500,
            sheets_conn=sheets_conn,
        )
        t.create()
        return t

    @pytest.mark.connection
    def test_formatting_applications(self, test_tab: Tab):
        rng = FullRange("A1:C3")
        test_tab.format_cell.add_alternating_row_background(Color(1.0, 0.5), rng)
        test_tab.format_text.apply_format(TextFormat(font_size=14, bold=True), rng)
        test_tab.commit()
        test_tab.get_data()
        a1 = test_tab.formats[0][0]
        assert a1["backgroundColor"]["red"] == 1
        assert a1["backgroundColor"]["green"] == 0.49803922
        assert a1["textFormat"]["bold"]
        assert a1["textFormat"]["fontSize"] == 14
        c2 = test_tab.formats[1][2]
        assert c2["backgroundColor"]["red"] == 1
        assert c2["backgroundColor"]["green"] == 1
        assert c2["textFormat"]["bold"]
        assert c2["textFormat"]["fontSize"] == 14
        # Test set_background_color:
        rng = FullRange("A5:C7")
        test_tab.format_cell.set_background_color(
            Color(0.5, 0.5, 0.5), rng
        ).set_border_format(style=BorderSolidThick, color=Color(0, 0, 1.0), rng=rng)
        test_tab.commit()
        test_tab.get_data()
        for row in test_tab.formats[4:]:
            for cell in row:
                bground_color = cell["backgroundColor"]
                assert bground_color["red"] == 0.49803922
                assert bground_color["green"] == 0.49803922
                assert bground_color["blue"] == 0.49803922
                borders = cell["borders"]
                for side in ["left", "right", "bottom", "top"]:
                    assert borders[side]["style"] == "SOLID_THICK"
                    assert borders[side]["color"] == {"blue": 1}
