from __future__ import annotations

from typing import Dict, List, Any

from .core import Component
from .interfaces import AuthConfig, TwoDRange, OneDRange
from .connection import SheetsConnection
from .formatting.formatting import (
    TabCellFormatting,
    TabGridFormatting,
    TabTextFormatting,
)
from . import google_terms as terms


class Tab(Component):
    def __init__(
        self,
        gsheet_id: str,
        tab_title: str,
        tab_idx: int,
        tab_id: int,
        column_count: int = 26,
        row_count: int = 1000,
        *,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> None:
        self._tab_id = tab_id
        self._title = tab_title
        self._index = tab_idx
        self._column_count = column_count
        self._row_count = row_count
        super().__init__(
            gsheet_id=gsheet_id,
            gsheet_range=TwoDRange(
                self._tab_id,
                start_row=0,
                end_row=row_count,
                start_col=0,
                end_col=column_count,
                tab_title=tab_title,
                base0_idxs=True,
            ),
            grid_formatting=TabGridFormatting,
            text_formatting=TabTextFormatting,
            cell_formatting=TabCellFormatting,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )

    @property
    def tab_id(self) -> int:
        return self._tab_id

    @property
    def format_grid(self) -> TabGridFormatting:
        return self._format_grid

    @property
    def title(self) -> str:
        return self._title

    @property
    def index(self) -> int:
        return self._index

    @property
    def column_count(self) -> int:
        return self._column_count

    @property
    def row_count(self) -> int:
        return self._row_count

    @classmethod
    def from_properties(
        cls,
        gsheet_id: str,
        properties: Dict[str, Any],
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> Tab:
        title = str(properties[terms.TAB_NAME])
        index = int(properties[terms.TAB_IDX])
        tab_id = int(properties[terms.TAB_ID])
        column_count = int(properties[terms.GRID_PROPS][terms.COL_CT])
        row_count = int(properties[terms.GRID_PROPS][terms.ROW_CT])
        return Tab(
            gsheet_id,
            tab_title=title,
            tab_idx=index,
            tab_id=tab_id,
            column_count=column_count,
            row_count=row_count,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )

    def two_d_range(self) -> TwoDRange:
        return TwoDRange(
            self._tab_id, 0, self._row_count, 0, self._column_count, base0_idxs=True
        )

    def get_data(self, rng: TwoDRange | OneDRange = None) -> Tab:
        rng = self.two_d_range() if not rng else rng
        self._values, self._formats = self._get_data(
            self._gsheet_id, f"{self._title}!{rng}"
        )
        return self

    def write_values(
        self, data: List[List[Any]], rng: TwoDRange | OneDRange = None
    ) -> Tab:
        rng = self.two_d_range() if not rng else rng
        self._write_values(data, dict(rng))
        return self

    @classmethod
    def new_tab_request(
        cls,
        tab_title: str,
        tab_id: int = None,
        tab_idx: int = None,
        num_rows: int = 1000,
        num_cols: int = 26,
    ) -> Dict[str, Any]:
        props: Dict[str, Any] = {
            terms.TAB_NAME: tab_title,
            terms.GRID_PROPS: {terms.COL_CT: num_cols, terms.ROW_CT: num_rows},
        }
        if tab_id is not None:
            props[terms.TAB_ID] = tab_id
        if tab_idx is not None:
            props[terms.TAB_IDX] = tab_idx
        result = {terms.ADDTAB: {terms.TAB_PROPS: props}}
        return result

    def gen_add_tab_request(self) -> Dict[str, Any]:
        return self.new_tab_request(
            self._title, self._tab_id, self._index, self._row_count, self._column_count
        )

    def create(self) -> Tab:
        req = self.new_tab_request(
            self.title, self.tab_id, self.index, self.row_count, self.column_count
        )
        self._requests.append(req)
        self.commit()
        return self
