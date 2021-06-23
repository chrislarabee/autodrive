from __future__ import annotations

from typing import Dict, Iterator, Any
from collections.abc import Mapping
from pathlib import Path

from . import google_terms as terms

DEFAULT_TOKEN = "gdrive_token.pickle"
DEFAULT_CREDS = "credentials.json"


class AuthConfig:
    def __init__(
        self,
        secrets_config: Dict[str, Any] = None,
        token_filepath: str | Path = DEFAULT_TOKEN,
        creds_filepath: str | Path = DEFAULT_CREDS,
    ) -> None:
        self.secrets_config = secrets_config
        self._token_filepath = Path(token_filepath)
        self._creds_filepath = Path(creds_filepath)

    @property
    def token_filepath(self) -> Path:
        return self._token_filepath

    @property
    def creds_filepath(self) -> Path:
        return self._creds_filepath


class RangeArgs(Mapping):
    def __init__(self, tab_id: int) -> None:
        self.tab_id = tab_id

    def to_dict(self) -> Dict[str, int]:
        return {terms.TAB_ID: self.tab_id}

    def __iter__(self) -> Iterator[int | str]:
        return iter(self.to_dict())

    def __getitem__(self, k: str) -> int | None:
        return self.to_dict().get(k)

    def __len__(self) -> int:
        return len(self.to_dict())


class OneDRange(RangeArgs):
    def __init__(self, tab_id: int, start_idx: int = None, end_idx: int = None) -> None:
        super().__init__(tab_id)
        self.start_idx = start_idx
        self.end_idx = end_idx

    # All of these must be is not None because any of them can be 0:
    def to_dict(self) -> Dict[str, int]:
        result = {terms.TAB_ID: self.tab_id}
        if self.start_idx is not None:
            result["startIndex"] = self.start_idx
        if self.end_idx is not None:
            result["endIndex"] = self.end_idx
        return result


class TwoDRange(RangeArgs):
    def __init__(
        self,
        tab_id: int,
        start_row: int = None,
        end_row: int = None,
        start_col: int = None,
        end_col: int = None,
    ) -> None:
        super().__init__(tab_id)
        self.start_row = start_row
        self.end_row = end_row
        self.start_col = start_col
        self.end_col = end_col

    def to_dict(self) -> Dict[str, int]:
        result = {terms.TAB_ID: self.tab_id}
        # All of these must be is not None because any of them can be 0:
        if self.start_row is not None:
            result["startRowIndex"] = self.start_row
        if self.end_row is not None:
            result["endRowIndex"] = self.end_row
        if self.start_col is not None:
            result["startColumnIndex"] = self.start_col
        if self.end_col is not None:
            result["endColumnIndex"] = self.end_col
        return result
