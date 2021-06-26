from __future__ import annotations

from typing import Dict, List, Any

from .core import Component
from .interfaces import AuthConfig, TwoDRange
from .connection import SheetsConnection
from .formatting import (
    RangeCellFormatting,
    RangeGridFormatting,
    RangeTextFormatting,
)


class Range(Component):
    def __init__(
        self,
        gsheet_range: TwoDRange,
        gsheet_id: str,
        tab_title: str,
        *,
        auth_config: AuthConfig = None,
        sheets_conn: SheetsConnection = None,
        autoconnect: bool = True,
    ) -> None:
        self._tab_title = tab_title
        gsheet_range.tab_title = tab_title
        self._rng = gsheet_range
        super().__init__(
            gsheet_id=gsheet_id,
            gsheet_range=gsheet_range,
            grid_formatting=RangeGridFormatting,
            text_formatting=RangeTextFormatting,
            cell_formatting=RangeCellFormatting,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )

    @property
    def format_grid(self) -> RangeGridFormatting:
        return self._format_grid

    @property
    def format_text(self) -> RangeTextFormatting:
        return self._format_text

    @property
    def format_cell(self) -> RangeCellFormatting:
        return self._format_cell

    def to_dict(self) -> Dict[str, int]:
        return dict(self._rng)

    def get_data(self) -> Range:
        self._values, self._formats = self._get_data(self._gsheet_id, str(self._rng))
        return self

    def write_values(self, data: List[List[Any]]) -> Range:
        self._write_values(data, self.to_dict())
        return self
