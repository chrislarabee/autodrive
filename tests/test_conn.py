from autodrive._conn import Connection


class TestConnection:
    def test_merge_dicts(self):
        expected = {"a": 1, "b": [1, 2, 3], "c": {"d": [1, 2, 3], "e": {"f": 100}}}
        dict1 = {"a": 2, "c": {"e": {"f": 100}}}
        dict2 = {"a": 1, "b": [1, 2, 3], "c": {"d": [1, 2, 3], "e": {"f": 100}}}
        assert Connection._merge_dicts(dict1, dict2) == expected

    def test_create_range_tuple_key(self):
        expected = (("sheetId", 0), ("startIndex", 1), ("endIndex", 5))
        result = Connection._create_range_tuple_key(
            {"endIndex": 5, "startIndex": 1, "sheetId": 0}
        )
        assert result == expected
        expected = (
            ("sheetId", 0),
            ("startRowIndex", 1),
            ("endRowIndex", 5),
            ("startColIndex", 5),
            ("endColIndex", 10),
        )
        result = Connection._create_range_tuple_key(
            {
                "endRowIndex": 5,
                "startColIndex": 5,
                "startRowIndex": 1,
                "sheetId": 0,
                "endColIndex": 10,
            }
        )

    def test_preprocess_requests(self):
        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": 123,
                        "startIndex": 0,
                        "endIndex": 5,
                    },
                    "fields": "userEnteredFormat",
                    "cell": {
                        "userEnteredFormat": {"borders": {"left": {"style": "SOLID"}}}
                    },
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": 123,
                        "startIndex": 0,
                        "endIndex": 5,
                    },
                    "fields": "userEnteredFormat",
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.0, "green": 1.0, "blue": 0.5}
                        }
                    },
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": 123,
                        "startIndex": 10,
                        "endIndex": 15,
                    },
                    "fields": "userEnteredFormat",
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.5}
                        }
                    },
                }
            },
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{"sheetId": 123, "startIndex": 10, "endIndex": 15}],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": [{"userEnteredVal": "=MOD(ROW(), 2)"}],
                            },
                            "format": {
                                "backgroundColor": {"red": 1.0, "green": 0.5},
                                "blue": 1.0,
                            },
                        },
                    },
                    "index": 10,
                }
            },
        ]
        expected = {
            "requests": [
                {
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [
                                {"sheetId": 123, "startIndex": 10, "endIndex": 15}
                            ],
                            "booleanRule": {
                                "condition": {
                                    "type": "CUSTOM_FORMULA",
                                    "values": [{"userEnteredVal": "=MOD(ROW(), 2)"}],
                                },
                                "format": {
                                    "backgroundColor": {"red": 1.0, "green": 0.5},
                                    "blue": 1.0,
                                },
                            },
                        },
                        "index": 10,
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": 123,
                            "startIndex": 0,
                            "endIndex": 5,
                        },
                        "fields": "userEnteredFormat",
                        "cell": {
                            "userEnteredFormat": {
                                "borders": {"left": {"style": "SOLID"}},
                                "backgroundColor": {
                                    "red": 0.0,
                                    "green": 1.0,
                                    "blue": 0.5,
                                },
                            }
                        },
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": 123,
                            "startIndex": 10,
                            "endIndex": 15,
                        },
                        "fields": "userEnteredFormat",
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 1.0,
                                    "green": 1.0,
                                    "blue": 0.5,
                                }
                            }
                        },
                    }
                },
            ]
        }
        result = Connection._preprocess_requests(requests)
        assert result == expected
