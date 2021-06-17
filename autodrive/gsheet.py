from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple


from .connection import SheetsConnection, AuthConfig

"""
THIS CAN BE DONE:
result = sheet.spreadsheets().batchUpdate(
    spreadsheetId=sheet_id, 
    body={
        'requests': [
            {
                'updateCells': {
                    'fields': '*', 
                    "rows": [
                        {
                            'values': [
                                {'userEnteredValue': {'numberValue': 1}}, 
                                {'userEnteredValue': {'numberValue': 2}}, 
                                {'userEnteredValue': {'numberValue': 3}}, 
                                {'userEnteredValue': {'numberValue': 4}}, 
                                {'userEnteredValue': {'numberValue': 5}}
                            ]
                        }
                    ], 
                    "range": {
                        "sheetId": 0, 
                        "startRowIndex": 25, 
                        "startColumnIndex": 0, 
                        "endColumnIndex": 5
                    }
                }
            }, 
            {
                'repeatCell': {
                    "fields": "userEnteredFormat(textFormat)", 
                    "range": {
                        "sheetId": 0, 
                        "startRowIndex": 25, 
                        "startColumnIndex": 0
                    }, 
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "fontSize": 14, 
                                "bold": True
                            }
                        }
                    }
                }
            }
        ]
    }
)
"""


"""
Structural Idea:

Drive:
    -m get (returns):
        GFolder?:
        GSheet:
            -a Tab Instances:
                -a Request List
                -a Formatting Instance (to add formatting requests):
                -a Values Instance (to add values requests):
                -m Execute (sends Request List)
            -a Default Tab attr (maps to GSheet._tabs[0])
            -m Execute (collects Tab Request Lists, combines them, and sends)
        GDoc?:
            
"""


class Tab:
    def __init__(
        self,
        values: List[Dict[str, Any]],
        tab_title: str = None,
        tab_index: int = None,
        parent_file_id: str = None,
        properties: Dict = None,
        parent: GSheet = None,
    ) -> None:
        if not properties:
            try:
                assert tab_title and tab_index and parent_file_id
            except AssertionError:
                raise ValueError(
                    "If metadata is None then tab_title, tab_index, and "
                    "parent_file_id are required."
                )
            else:
                properties = dict(
                    title=tab_title, index=tab_index, sheetId=parent_file_id
                )
        self._title = str(properties["title"])
        self._index = int(properties["index"])
        self._file_id = str(properties["sheetId"])
        self._values = self.parse_row_data(values)
        self._parent = parent

    @property
    def title(self) -> str:
        return self._title

    @property
    def index(self) -> int:
        return self._index

    @property
    def values(self) -> List[List[Any]]:
        return self._values

    @staticmethod
    def parse_row_data(
        row_data: List[Dict[str, List[Dict[str, Any]]]]
    ) -> List[List[Any]]:
        results = []
        for row in row_data:
            row_list = []
            for cell in row.get("values", []):
                user_entered_value = cell.get("userEnteredValue")
                if user_entered_value:
                    for key in ["stringValue", "formulaValue", "numberValue"]:
                        value = user_entered_value.get(key)
                        if value:
                            row_list.append(value)
                else:
                    row_list.append(None)
            results.append(row_list)
        return results


class GSheet:
    def __init__(
        self,
        file_id: str,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
    ) -> None:
        self._conn = sheets_conn or SheetsConnection(auth_config=auth_config)
        self._tabs = []
        self._file_id = file_id
        self._requests: List[Dict[str, Any]] = []

    @property
    def requests(self) -> List[Dict[str, Any]]:
        return self._requests

    @property
    def tabs(self) -> Dict[str, Tab]:
        return {tab.title: tab for tab in self._tabs}

    def commit(self) -> None:
        self._conn.execute_requests(self._file_id, self._requests)
        self._requests = []

    def add_tab(self, title: str, index: int = None) -> GSheet:
        if title in self.tabs.keys():
            raise ValueError(f"Sheet already has tab with title {title}")
        self._requests.append(
            {"addSheet": {"properties": {"title": title, "index": index or 0}}}
        )
        return self

    def get_tab_index_by_title(self, tab_title: str) -> Optional[int]:
        for t in self._tabs:
            if t.title == tab_title:
                return t.index
        else:
            return None
