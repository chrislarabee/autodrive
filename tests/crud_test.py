import pytest

from autodrive.range import Range
from autodrive.tab import Tab
from autodrive.interfaces import TextFormat


class TestCRUD:
    @pytest.fixture
    def input_data(self):
        return [[1, 2, 3], [4, 5, 6]]

    def test_that_gsheet_can_write_and_read_values(self, test_gsheet, input_data):
        test_gsheet.write_values(input_data)
        test_gsheet.commit()
        test_gsheet.get_data()
        test_gsheet.tabs
        assert test_gsheet[0].values == input_data

    def test_that_range_can_write_and_read_values(
        self, test_gsheet, sheets_conn, input_data
    ):
        rng = Range(
            "Sheet1!A4:C5",
            tab_id=0,
            tab_title="",
            gsheet_id=test_gsheet.gsheet_id,
            sheets_conn=sheets_conn,
        )
        rng.write_values(input_data)
        rng.format_text.apply_format(TextFormat(font_size=14, bold=True))
        rng.commit()
        rng.get_data()
        assert rng.formats[0][0]["textFormat"]["fontSize"] == 14
        assert rng.formats[0][0]["textFormat"]["bold"]
        assert rng.values == input_data

    def test_that_tab_can_write_and_read_values(
        self, test_gsheet, sheets_conn, input_data
    ):
        tab = Tab(
            test_gsheet.gsheet_id,
            tab_title="test_sheet",
            tab_idx=1,
            tab_id=123456789,
            sheets_conn=sheets_conn,
        )
        tab.create()
        tab.write_values(input_data)
        tab.commit()
        tab.get_data()
        assert tab.values == input_data
