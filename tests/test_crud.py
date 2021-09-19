from typing import List

import pytest

from autodrive.gsheet import GSheet
from autodrive.range import Range
from autodrive.tab import Tab
from autodrive.interfaces import FullRange
from autodrive.connection import SheetsConnection


@pytest.mark.connection
class TestCRUD:
    @pytest.fixture
    def input_data(self):
        return [[1, 2, 3], [4, 5, 6]]

    def test_that_gsheet_can_write_and_read_values(
        self, test_gsheet: GSheet, input_data: List[List[int]]
    ):
        test_gsheet.write_values(input_data)
        test_gsheet.commit()
        test_gsheet.get_data()
        test_gsheet.tabs
        assert test_gsheet[0].values == input_data

    def test_that_range_can_write_and_read_values(
        self,
        test_gsheet: GSheet,
        sheets_conn: SheetsConnection,
        input_data: List[List[int]],
    ):
        rng = Range(
            FullRange("A4:C5"),
            tab_title="Sheet1",
            tab_id=0,
            gsheet_id=test_gsheet.gsheet_id,
            sheets_conn=sheets_conn,
        )
        rng.write_values(input_data)
        rng.commit()
        rng.get_data()
        assert rng.values == input_data

    def test_that_tab_can_write_and_append_and_read_values(
        self,
        test_gsheet: GSheet,
        sheets_conn: SheetsConnection,
        input_data: List[List[int]],
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
        tab.write_values(input_data, mode="a")
        tab.commit()
        tab.get_data()
        assert len(tab.values) == 4
        assert tab.values == [*input_data, *input_data]
