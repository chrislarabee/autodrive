from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple

from googleapiclient.discovery import Resource


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
        self._parent = parent

    @property
    def title(self) -> str:
        return self._title

    @property
    def index(self) -> int:
        return self._index

    @staticmethod
    def parse_row_data(row_data: List[Dict[str, List[Dict[str, Any]]]]) -> List[List[Any]]:
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
    def __init__(self, file_id: str, tabs: List[Tab], parent=None) -> None:
        self._tabs = tabs
        self._file_id = file_id
        self._parent = parent
        self._requests = []

    @property
    def tabs(self) -> Dict[str, Tab]:
        return {tab.title: tab for tab in self._tabs}

    def execute(self) -> None:
        """
        Executes the amassed requests on this GSheet object.

        Returns: None

        """
        if self._parent:
            self._parent.batch_update(self._file_id, self._requests)

    # TODO: Make it so this can create a tab at a specific index?
    def add_tab(self, title: str) -> GSheet:
        """
        Adds a new sheet to the Google Sheet at the passed id.

        Args:
            sheet_id: The id of a Google Sheet.
            **sheet_properties: The desired properties of the new
                sheet, such as:
                    title: The title of the sheet.

        Returns: The title and index position of the new sheet.

        """
        if title in self.tabs.keys():
            raise ValueError(f"Sheet already has tab with title {title}")
        else:
            self._tabs.append(Tab(title, len(self._tabs), self._file_id))
        request = dict(addSheet=dict(properties=dict(title=title)))
        self._requests.append(request)
        return self

    def get_tab_index_by_title(self, tab_title: str) -> Optional[int]:
        for t in self._tabs:
            if t.title == tab_title:
                return t.index
        else:
            return None
