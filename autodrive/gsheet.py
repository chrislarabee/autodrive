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


class GSheetError(Exception):
    pass


class Tab:
    def __init__(
        self,
        parent: GSheet,
        tab_title: str = None,
        tab_index: int = None,
        properties: Dict[str, Any] = None,
    ) -> None:
        if not properties:
            if tab_title and tab_index:
                properties = dict(title=tab_title, index=tab_index)
            else:
                raise ValueError(
                    "If properties is None then tab_title and tab_index are "
                    "required."
                )
        self._parent = parent
        self._title = str(properties["title"])
        self._index = int(properties["index"])
        self._values = []

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


class PartialGSheet:
    def __init__(self, file_id: str, title: str, sheets_conn: SheetsConnection) -> None:
        self._conn = sheets_conn
        self._file_id = file_id
        self._title = title

    def fetch(self) -> GSheet:
        return GSheet.from_id(self._file_id, sheets_conn=self._conn)


class GSheet:
    def __init__(
        self,
        file_id: str,
        title: str = None,
        tabs: List[Tab] = None,
        *,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
    ) -> None:
        self._conn = sheets_conn or SheetsConnection(auth_config=auth_config)
        self._file_id = file_id
        self._title = title
        self._tabs = tabs or []
        self._requests: List[Dict[str, Any]] = []
        self._partial = True

    @property
    def requests(self) -> List[Dict[str, Any]]:
        return self._requests

    @property
    def tabs(self) -> Dict[str, Tab]:
        return {tab.title: tab for tab in self._tabs}

    @classmethod
    def from_id(
        cls,
        file_id: str,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
    ) -> GSheet:
        gs = GSheet(file_id, auth_config=auth_config, sheets_conn=sheets_conn)
        return gs.fetch()

    def fetch(self) -> GSheet:
        properties = self._conn.get_properties(self._file_id)
        name, sheets = self._parse_properties(properties)
        self._name = name
        tabs = []
        for sheet in sheets:
            tabs.append(
                Tab(
                    parent=self,
                    tab_title=sheet["title"],
                    tab_index=sheet["index"],
                )
            )
        self._tabs = tabs
        self._partial = False
        return self

    @staticmethod
    def _parse_properties(
        properties: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        sheet_title = properties["properties"]["title"]
        sheet_props = [sheet["properties"] for sheet in properties["sheets"]]
        return sheet_title, sheet_props

    def commit(self) -> None:
        self._conn.execute_requests(self._file_id, self._requests)
        self._requests = []

    def add_tab(self, title: str, index: int = None) -> GSheet:
        self._ensure_not_partial()
        if title in self.tabs.keys():
            raise ValueError(f"Sheet already has tab with title {title}")
        self._requests.append(
            {"addSheet": {"properties": {"title": title, "index": index or 0}}}
        )
        return self

    def _ensure_not_partial(self) -> None:
        if self._partial:
            raise GSheetError(
                f"PartialGSheetError: {self} is only partially instantiated. This "
                "method cannot be called. Execute .fetch() to resolve this error."
            )

    def get_tab_index_by_title(self, tab_title: str) -> Optional[int]:
        for t in self._tabs:
            if t.title == tab_title:
                return t.index
        else:
            return None
