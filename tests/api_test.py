from gsheet_api.api import API


class TestAPI:
    def test_connect(self):
        connections = API().connect()
        assert len(connections) == 2