import os
import warnings

import pytest

from autodrive.connection import (
    DriveConnection,
    SheetsConnection,
    DEFAULT_CREDS,
    DEFAULT_TOKEN,
)
from autodrive.gsheet import Component, GSheet, Tab
from .testing_tools import CREATED_IDS


conn_warning = (
    "No {0} or {1} found in {2}. Autodrive is not being fully tested. To execute "
    "all tests properly download google api credentials as described in the README."
)


@pytest.fixture(scope="session")
def drive_conn():
    if os.path.exists(DEFAULT_TOKEN) or os.path.exists(DEFAULT_CREDS):
        conn = DriveConnection()
        yield conn
        # warnings.warn("Cleaning up google drive objects created for tests...")
        ids = CREATED_IDS
        for i in ids:
            conn.delete_object(i)
        # warnings.warn(f"Successfully cleaned up {len(ids)} objects.")
    else:
        warnings.warn(conn_warning.format(DEFAULT_CREDS, DEFAULT_TOKEN, os.getcwd()))
        return None


@pytest.fixture(scope="session")
def sheets_conn():
    if os.path.exists(DEFAULT_TOKEN) or os.path.exists(DEFAULT_CREDS):
        conn = SheetsConnection()
        yield conn
        # warnings.warn("Cleaning up google drive objects created for tests...")
        ids = CREATED_IDS
        # for i in ids:
        #     conn.delete_object(i)
        # warnings.warn(f"Successfully cleaned up {len(ids)} objects.")
    else:
        warnings.warn(conn_warning.format(DEFAULT_CREDS, DEFAULT_TOKEN, os.getcwd()))
        return None


class GSheetComponent(Component):
    pass


@pytest.fixture
def testing_component():
    return GSheetComponent


@pytest.fixture(scope="session")
def test_gsheet(sheets_conn):
    return GSheet(
        "test",
        "test",
        sheets_conn=sheets_conn,
    )


@pytest.fixture(scope="session")
def test_tab(sheets_conn, test_gsheet):
    return Tab(
        parent_gsheet=test_gsheet,
        properties={
            "title": "Sheet1",
            "index": 0,
            "gridProperties": {"columnCount": 10, "rowCount": 500},
        },
        sheets_conn=sheets_conn,
    )
