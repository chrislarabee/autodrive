import os
import warnings

import pytest

from autodrive.connection import DriveConnection, DEFAULT_CREDS, DEFAULT_TOKEN
from .testing_tools import CREATED_IDS


@pytest.fixture(scope="session")
def drive_conn():
    if os.path.exists(DEFAULT_TOKEN) or os.path.exists(DEFAULT_CREDS):
        conn = DriveConnection()
        yield conn
        warnings.warn("Cleaning up google drive objects created for tests...")
        ids = CREATED_IDS
        for i in ids:
            conn.delete_object(i)
        warnings.warn(f"Successfully cleaned up {len(ids)} objects.")
    else:
        warnings.warn(
            f"No {DEFAULT_CREDS} or {DEFAULT_TOKEN} found in {os.getcwd()}. "
            "The API is not being fully tested. To execute all tests properly "
            "download google api credentials as described in the README."
        )
        return None
