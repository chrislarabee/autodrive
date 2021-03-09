import os
import warnings

import pytest

from gsheet_api.api import GSheetsAPI
from .testing_tools import CREATED_IDS


@pytest.fixture(scope="session")
def api():
    if os.path.exists("token.pickle") or os.path.exists("credentials.json"):
        api = GSheetsAPI()
        api.connect()
        yield api
        warnings.warn("Cleaning up google drive objects created for tests...")
        ids = CREATED_IDS
        for i in ids:
            api.delete_object(i)
        warnings.warn(f"Successfully cleaned up {len(ids)} objects.")
    else:
        warnings.warn(
            f"No credentials.json or token.pickle found in {os.getcwd()}. The "
            "API is not being fully tested. To execute all tests properly "
            "download google api credentials as described in the README."
        )
        return None
