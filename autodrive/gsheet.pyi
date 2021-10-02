from ._view import GSheetView as GSheetView
from .connection import SheetsConnection as SheetsConnection
from .dtypes import EffectiveVal as EffectiveVal, GoogleValueType as GoogleValueType
from .interfaces import AuthConfig as AuthConfig, FullRange as FullRange
from .range import Range as Range
from .tab import Tab as Tab
from pathlib import Path
from typing import (
    Any,
    Dict,
    KeysView,
    List,
    Literal,
    Optional,
    Sequence,
    ValuesView,
    Union,
)

class GSheet(GSheetView):
    _title: Any = ...
    _tabs: Any = ...
    def __init__(
        self,
        gsheet_id: str,
        title: Union[str, None] = ...,
        *,
        tabs: Union[List[Tab], None] = ...,
        auth_config: Union[AuthConfig, None] = ...,
        sheets_conn: Union[SheetsConnection, None] = ...,
        autoconnect: bool = ...
    ) -> None: ...
    @property
    def requests(self) -> List[Dict[str, Any]]: ...
    @property
    def tabs(self) -> Dict[str, Tab]: ...
    @property
    def title(self) -> Optional[str]: ...
    def fetch(self) -> GSheet: ...
    def add_tab(self, tab: Tab) -> GSheet: ...
    def gen_range(self, rng: FullRange, tab: Union[str, int, None] = ...) -> Range: ...
    def write_values(
        self,
        data: Sequence[Union[Sequence[Any], Dict[str, Any]]],
        to_tab: Union[str, None] = ...,
        rng: Union[FullRange, str, None] = ...,
        mode: Literal["write", "w", "append", "a"] = ...,
    ) -> GSheet: ...
    def get_data(
        self,
        tab: Union[str, int, None] = ...,
        rng: Union[FullRange, str, None] = ...,
        value_type: GoogleValueType = ...,
    ) -> GSheet: ...
    def __iter__(self) -> Any: ...
    def __len__(self) -> int: ...
    def __getitem__(self, key: Union[int, str]) -> Tab: ...
    def keys(self) -> KeysView[str]: ...
    def values(self) -> ValuesView[Tab]: ...
    def get_tab_index_by_title(self, tab_title: str) -> Optional[int]: ...
    def to_csv(
        self,
        root_path: Union[str, Path],
        filename_overrides: Union[Dict[str, str], None] = ...,
        **tabs_and_headers: Union[Sequence[Any], None]
    ) -> None: ...
    def to_json(
        self,
        root_path: Union[str, Path],
        filename_overrides: Union[Dict[str, str], None] = ...,
        **tabs_and_headers: Union[Sequence[str], int]
    ) -> None: ...
