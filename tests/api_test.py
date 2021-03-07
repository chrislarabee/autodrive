from datetime import datetime as dt

from gsheet_api.api import GSheetsAPI
from . import testing_tools

class TestAPI:
    def test_connect(self):
        connections = GSheetsAPI().connect()
        assert len(connections) == 2

    class TestDrive:
        class TestCreateObject:
            def test_create_folder(self, api):
                folder = f"gsheet_api_test_folder {dt.now()}"
                f_id = api.drive.create_object(folder, "folder")
                testing_tools.CREATED_IDS.append(f_id)
                f = api.drive.find_object(folder, "folder")
                assert len(f) > 0
                assert f[0].get("name") == folder