import pytest

from autodrive.connection import SheetsConnection
from autodrive.gsheet import GSheet
from autodrive.interfaces import HalfRange
from autodrive.tab import Tab


class TestTabFormatting:
    @pytest.mark.connection
    def test_grid_formatting_applications(
        self, test_gsheet: GSheet, sheets_conn: SheetsConnection
    ):
        tab = Tab(
            test_gsheet.gsheet_id,
            tab_title="tab_format",
            tab_id=11,
            tab_idx=0,
            column_count=10,
            row_count=500,
            sheets_conn=sheets_conn,
        )
        tab.create()
        (
            tab.format_grid.append_rows(5)
            .delete_rows(HalfRange(5, 7))
            .insert_rows(1, 1)
            .append_columns(10)
            .delete_columns(HalfRange(10, 14))
            .insert_columns(2, 7)
        )
        tab.commit()
        tab.fetch()
        assert tab.row_count == 504
        assert tab.column_count == 18
