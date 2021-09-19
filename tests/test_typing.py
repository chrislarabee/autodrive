from autodrive.interfaces import FullRange
from autodrive import typing
from autodrive.range import Range
from autodrive.tab import Tab
from autodrive.gsheet import GSheet
from autodrive.connection import SheetsConnection, DriveConnection


def test_that_type_assertions_work():
    rng = Range(
        FullRange("A1"),
        gsheet_id="test",
        tab_id=0,
        tab_title="sheet1",
        autoconnect=False,
    )
    tab = Tab("test", "sheet1", 0, 0, autoconnect=False)
    gsheet = GSheet("test", "test", autoconnect=False)
    assert isinstance(rng, typing.View)
    assert isinstance(tab, typing.View)
    assert isinstance(gsheet, typing.View)


def test_that_they_work_in_annotations():
    def _test_func(comp: typing.Connection):
        return comp

    SConn = SheetsConnection()
    DConn = DriveConnection()

    _ = _test_func(SConn)
    _ = _test_func(DConn)
