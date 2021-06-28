import os
import warnings
from datetime import datetime as dt

import pytest

from autodrive.connection import (
    DriveConnection,
    SheetsConnection,
)
from autodrive.gsheet import GSheetView, GSheet
from autodrive.interfaces import DEFAULT_CREDS, DEFAULT_TOKEN
from .testing_tools import CREATED_IDS


conn_warning = (
    "No {0} or {1} found in {2}. Autodrive is not being fully tested. To execute "
    "all tests properly download google api credentials as described in the README."
)


@pytest.fixture(scope="session")
def drive_conn():
    if (
        DriveConnection.get_creds_from_env()
        or os.path.exists(DEFAULT_TOKEN)
        or os.path.exists(DEFAULT_CREDS)
    ):
        conn = DriveConnection()
        yield conn
        # warnings.warn("Cleaning up google drive objects created for tests...")
        ids = CREATED_IDS
        for i in ids:
            conn.delete_object(i)
        # warnings.warn(f"Successfully cleaned up {len(ids)} objects.")
    else:
        warnings.warn(conn_warning.format(DEFAULT_CREDS, DEFAULT_TOKEN, os.getcwd()))
        yield None


@pytest.fixture(scope="session")
def sheets_conn():
    if (
        SheetsConnection.get_creds_from_env()
        or os.path.exists(DEFAULT_TOKEN)
        or os.path.exists(DEFAULT_CREDS)
    ):
        conn = SheetsConnection()
        yield conn
    else:
        warnings.warn(conn_warning.format(DEFAULT_CREDS, DEFAULT_TOKEN, os.getcwd()))
        yield None


class ExampleView(GSheetView):
    pass


@pytest.fixture
def gsheet_view():
    return ExampleView


@pytest.fixture(scope="session")
def test_gsheet(drive_conn: DriveConnection, sheets_conn: SheetsConnection):
    title = f"autodrive_test_sheet-{dt.now()}"
    if drive_conn:
        id_str = drive_conn.create_object(title, "sheet")
        CREATED_IDS.insert(0, id_str)
        gsheet = GSheet(
            id_str,
            title,
            sheets_conn=sheets_conn,
        )
        gsheet.fetch()
        return gsheet
    else:
        return GSheet(
            "test",
            title,
            sheets_conn=sheets_conn,
        )
