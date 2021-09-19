from autodrive.tab import Tab


class TestTab:
    def test_that_new_tab_requests_generates_proper_request(self):
        assert Tab.new_tab_request("test", 1234, 0, 500, 10) == {
            "addSheet": {
                "properties": {
                    "title": "test",
                    "gridProperties": {
                        "rowCount": 500,
                        "columnCount": 10,
                    },
                    "sheetId": 1234,
                    "index": 0,
                }
            }
        }
        assert Tab.new_tab_request("test") == {
            "addSheet": {
                "properties": {
                    "title": "test",
                    "gridProperties": {
                        "rowCount": 1000,
                        "columnCount": 26,
                    },
                }
            }
        }
