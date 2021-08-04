from __future__ import annotations

import string
from abc import ABC
from typing import Any, Dict, Generic, List, Tuple, Type, TypeVar, Sequence
from pathlib import Path
import csv
import jsonlines  # type: ignore

from . import _google_terms as terms
from .connection import SheetsConnection
from .dtypes import (
    GOOGLE_DTYPES,
    TYPE_MAP,
    EffectiveFmt,
    EffectiveVal,
    Formula,
    String,
    GoogleValueType,
    UserEnteredVal,
)
from .interfaces import AuthConfig, FullRange
from ._core import GoogleDtype

T = TypeVar("T", bound="GSheetView")
FC = TypeVar("FC", bound="CellFormatting")
FG = TypeVar("FG", bound="GridFormatting")
FT = TypeVar("FT", bound="TextFormatting")


class NoConnectionError(Exception):
    """
    Error thrown when attempting to connect via a SheetsConnection that does not
    exist.
    """

    def __init__(self, vtype: Type[GSheetView], *args: object) -> None:
        msg = f"No SheetsConnection has been established for this {vtype}."
        super().__init__(msg, *args)


class OutputError(Exception):
    """
    Error thrown when something goes wrong when attempting to write values to a
    file.
    """


class Formatting:
    """
    Formatting objects contain methods for adding various update format requests
    to their parent Component.
    """

    def __init__(self, parent: Component[Any, Any, Any]):
        """

        Args:
            parent (Component[Any, Any, Any]): A Component object.

        """
        self._parent = parent

    def add_request(self, request: Dict[str, Any]) -> None:
        """
        Adds the passed request to the Formatting object's parent component.

        Args:
          request (Dict[str, Any]): An api-ready request.

        """
        self._parent.requests.append(request)

    def ensure_full_range(self, rng: FullRange | None = None) -> FullRange:
        """
        Convenience method for ensuring that all requests generated by this
        Formatting object have a FullRange attached to them, if one isn't manually
        supplied.

        Args:
          rng (FullRange, optional): A manually generated FullRange, defaults to None.

        Returns:
          FullRange: The passed FullRange, or a range generated from the Formatting
          object's parent Component.

        """
        return rng if rng else self._parent.range


class CellFormatting(Formatting):
    """
    Contains methods for generating format requests that update cell properties.
    """

    ...


class GridFormatting(Formatting):
    """
    Contains methods for generating format requests that update grid properties.
    """

    ...


class TextFormatting(Formatting):
    """
    Contains methods for generating format requests that update the properties of
    text in one or more cells.
    """

    ...


class GSheetView(ABC):
    """
    Abstract base class for the different ways of viewing a Google Sheet.
    """

    def __init__(
        self,
        gsheet_id: str,
        *,
        auth_config: AuthConfig | None = None,
        sheets_conn: SheetsConnection | None = None,
        autoconnect: bool = True,
    ) -> None:
        """

        Args:
            gsheet_id (str): The id string of the target Google Sheet that the View
                is attached to.
            auth_config (AuthConfig, optional): Optional custom AuthConfig, defaults
                to None.
            sheets_conn (SheetsConnection, optional): Optional manually created
                SheetsConnection, defaults to None.
            autoconnect (bool, optional): If you want to instantiate a View without
                immediately checking your authentication credentials and connection
                to the Google Sheets api, set this to False, defaults to True.
        """
        super().__init__()
        if not sheets_conn and autoconnect:
            sheets_conn = SheetsConnection(auth_config=auth_config)
        self._conn = sheets_conn
        self._auth = auth_config
        self._gsheet_id = gsheet_id
        self._requests: List[Dict[str, Any]] = []

    @property
    def requests(self) -> List[Dict[str, Any]]:
        """
        Returns:
            List[Dict[str, Any]]: The list of current (uncommitted) requests.

        """
        return self._requests

    @property
    def conn(self) -> SheetsConnection:
        """
        Returns:
            SheetsConnection: The view's SheetsConnection.

        Raises:
            NoConnectionError: If the view's connection is null.

        """
        if not self._conn:
            raise NoConnectionError(type(self))
        return self._conn

    @property
    def auth(self) -> AuthConfig:
        """
        Returns:
            AuthConfig: The view's AuthConfig.

        Raises:
            NoConnectionError: If the view's auth config is null.

        """
        if not self._auth:
            raise NoConnectionError(type(self))
        return self._auth

    @property
    def gsheet_id(self) -> str:
        """
        Returns:
            str: The id of the Google Sheet this view is connected to.

        """
        return self._gsheet_id

    def commit(self) -> Dict[str, Any]:
        """
        Commits the amassed requests on this view, sending them to the Sheets api
        as a batch update request.

        Returns:
            Dict[str, Any]: The response from the api.

        Raises:
            NoConnectionError: If the view's SheetsConnection is null.

        """
        if not self._conn:
            raise NoConnectionError(type(self))
        results = self._conn.execute_requests(self._gsheet_id, self._requests)
        self._requests = []
        return results

    @staticmethod
    def _parse_properties(
        properties: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        sheet_title = properties[terms.FILE_PROPS][terms.FILE_NAME]
        sheet_props = [sheet[terms.TAB_PROPS] for sheet in properties[terms.TABS_PROP]]
        return sheet_title, sheet_props

    @classmethod
    def _parse_row_data(
        cls,
        row_data: List[Dict[str, List[Dict[str, Any]]]],
        value_type: GoogleValueType = EffectiveVal,
    ) -> Tuple[List[List[Any]], List[List[Dict[str, Any]]]]:
        """
        Parses the dictionary returned by SheetsConnection.get_data and extracts
        only the relevant data.

        Args:
            row_data (List[Dict[str, List[Dict[str, Any]]]]): The raw data to parse.
            value_type (GoogleValueType, optional): The value representation to
                extract from the raw data, defaults to EffectiveVal

        Returns:
            Tuple[List[List[Any]], List[List[Dict[str, Any]]]]: A tuple containing
            a list of extracted data and another list of extracted formatting
            information.

        """
        values: List[List[Any]] = []
        formats: List[List[Dict[str, Any]]] = []
        for row in row_data:
            value_list: List[Any] = []
            fmt_list: List[Dict[str, Any]] = []
            for cell in row.get(terms.VALUES, []):
                raw_value = cell.get(str(value_type))
                fmt = cell.get(str(EffectiveFmt), {})
                value = raw_value
                if value_type in (UserEnteredVal, EffectiveVal):
                    if raw_value:
                        for dtype in GOOGLE_DTYPES:
                            value = raw_value.get(str(dtype))
                            if value:
                                if value_type == UserEnteredVal:  # type: ignore
                                    value = dtype.parse(value)
                                break
                value_list.append(value)
                fmt_list.append(fmt)
            values.append(value_list)
            formats.append(fmt_list)
        return values, formats

    def _get_data(
        self,
        gsheet_id: str,
        rng_str: str,
        value_type: GoogleValueType = EffectiveVal,
    ) -> Tuple[List[List[Any]], List[List[Dict[str, Any]]]]:
        """
        Fetches data from the view's SheetsConnection for the specified Google
        Sheet and parses it.

        Args:
            gsheet_id (str): The Google Sheet to fetch data from.
            rng_str (str: str): The range within the Google Sheet to fetch data from.
            value_type (GoogleValueType, optional): The value representation to
                extract from the raw data, defaults to EffectiveVal

        Returns:
            Tuple[List[List[Any]], List[List[Dict[str, Any]]]]: A tuple containing
            a list of data values and another list of formatting information.

        """
        raw = self.conn.get_data(gsheet_id, [rng_str])
        row_data = raw[terms.TABS_PROP][0][terms.DATA][0].get(terms.ROWDATA, [])
        return self._parse_row_data(row_data, value_type=value_type)

    def _write_values(
        self: T,
        data: Sequence[Sequence[Any] | Dict[str, Any]],
        tab_id: int,
        rng_dict: Dict[str, int],
    ) -> T:
        """
        Generates an update cells request for writing values to the target range.

        Args:
            data (Sequence[Sequence[Any] | Dict[str, Any]]): The data to write.
            rng_dict (Dict[str, int]): The range properties to write to.

        Returns:
            T: This Formatting object.

        """
        write_values: List[List[Dict[str, Any]]] = []
        for row in data:
            if isinstance(row, dict):
                if len(write_values) == 0:
                    write_values.append(
                        [self._gen_cell_write_value(k) for k in row.keys()]
                    )
                std_row = [val for val in row.values()]
            else:
                std_row = [val for val in row]
            write_values.append([self._gen_cell_write_value(val) for val in std_row])
        request = {
            "updateCells": {
                terms.FIELDS: "*",
                terms.ROWS: [{terms.VALUES: values} for values in write_values],
                terms.RNG: {terms.TAB_ID: tab_id, **rng_dict},
            }
        }
        self._requests.append(request)
        return self

    @staticmethod
    def _gen_cell_write_value(python_val: Any) -> Dict[str, Any]:
        """
        Converts a python value to its corresponding Google Dtype and wraps it in
        the key-value payload expected by the Sheets api.

        Args:
            python_val (Any): Any value. Only numeric values, booleans, and
                "formulas" (strings that start with =) will be converted. All
                other python data will be converted to its string representation.

        Returns:
            Dict[str, Any]: A dictionary containing the details the Sheet's api
            expects when writing data.

        """
        dtype: GoogleDtype
        type_ = type(python_val)
        if (
            isinstance(python_val, str)
            and len(python_val) >= 2
            and python_val[0] == "="
        ):
            dtype = Formula
        else:
            dtype = TYPE_MAP.get(type_, String)
        return {UserEnteredVal.value_key: {dtype.type_key: python_val}}

    # TODO: Delete this?
    @staticmethod
    def gen_alpha_keys(num: int) -> List[str]:
        """
        Generates a list of characters from the Latin alphabet a la gsheet/excel
        headers.

        Args:
            num (int): The desired length of the list.

        Returns:
            List[str]: A list containing as many letters and letter combos as
            desired. Can be used to generate sets up to 676 in length.

        """
        a = string.ascii_uppercase
        result: List[str] = list()
        x = num // 26
        for i in range(x + 1):
            root = a[i - 1] if i > 0 else ""
            keys = [root + a[j] for j in range(26)]
            for k in keys:
                result.append(k) if len(result) < num else None
        return result


class Component(GSheetView, Generic[FC, FG, FT]):
    """
    Base class for Tab and Range.
    """

    def __init__(
        self,
        *,
        gsheet_range: FullRange,
        gsheet_id: str,
        tab_id: int,
        grid_formatting: Type[FG],
        text_formatting: Type[FT],
        cell_formatting: Type[FC],
        auth_config: AuthConfig | None = None,
        sheets_conn: SheetsConnection | None = None,
        autoconnect: bool = True,
    ) -> None:
        super().__init__(
            gsheet_id,
            auth_config=auth_config,
            sheets_conn=sheets_conn,
            autoconnect=autoconnect,
        )
        self._rng = gsheet_range
        self._tab_id = tab_id
        self._values: List[List[Any]] = []
        self._formats: List[List[Dict[str, Any]]] = []
        self._format_grid = grid_formatting(self)
        self._format_text = text_formatting(self)
        self._format_cell = cell_formatting(self)

    @property
    def tab_id(self) -> int:
        """
        Returns:
            int: The id of the linked tab.

        """
        return self._tab_id

    @property
    def range_str(self) -> str:
        """
        str: The string representation of the range specified by this Component.

        """
        return str(self._rng)

    @property
    def range(self) -> FullRange:
        """
        Returns:
            FullRange: The FullRange representation of the range specified by this
            Component.

        """
        return self._rng

    @property
    def format_grid(self) -> FG:
        """
        Returns:
            FG: The GridFormatting subclass associated with this Component type.

        """
        return self._format_grid

    @property
    def format_text(self) -> FT:
        """
        Returns:
            FT: The TextFormatting subclass associated with this Component type.

        """
        return self._format_text

    @property
    def format_cell(self) -> FC:
        """
        Returns:
            FC: The CellFormatting subclass associated with this Component type.

        """
        return self._format_cell

    @property
    def values(self) -> List[List[Any]]:
        """
        Returns:
            List[List[Any]]: The fetched data values in this Component's cells.

        """
        return self._values

    @values.setter
    def values(self, new_values: List[List[Any]]) -> None:
        """
        Args:
            new_values (List[List[Any]]): The values to overwrite this Component's
                current values with.

        """
        self._values = new_values

    @property
    def formats(self) -> List[List[Dict[str, Any]]]:
        """
        Returns:
            List[List[Dict[str, Any]]]: The fetched formatting properties of this
            Component's cells.

        """
        return self._formats

    @formats.setter
    def formats(self, new_formats: List[List[Dict[str, Any]]]) -> None:
        """
        Args:
            new_formats (List[List[Dict[str, Any]]]): The formats to overwrite this
                Component's current formats with.

        """
        self._formats = new_formats

    @property
    def data_shape(self) -> Tuple[int, int]:
        """
        Returns:
            Tuple[int, int]: The row length and column width of this Component's
            data.

        """
        width = len(self._values[0]) if self._values else 0
        return len(self._values), width

    def to_csv(self, p: str | Path, header: Sequence[Any] | None = None) -> None:
        """
        Saves values to a csv file.

        Args:
            p (str | Path): The path-like for the file to save the data to.
            header (Sequence[Any], optional): A header row. If supplied, must be
                the same number of columns as the data values. Defaults to None.
        """
        if header:
            self._verify_header_len(header)
            values = [list(header), *self._values]
        else:
            values = self._values
        with open(p, "w") as file:
            writer = csv.writer(file)
            writer.writerows(values)

    def to_json(self, p: str | Path, header: Sequence[str] | int = 0) -> None:
        """
        Saves values to a json file, with one json per line.

        Args:
            p (str | Path): The path-like for the file to save the data to.
            header (Sequence[Any] | int): A header row or the index of a row in
                the values data to use as the header row. The header will be used
                as the keys for the json-formatted dictionaries. Defaults to 0,
                using the first row as the header.
        """
        if isinstance(header, Sequence):
            self._verify_header_len(header)
            values = self._values
        else:
            values = self.values
            header = values.pop(header)
        values_dicts = [dict(zip(header, row)) for row in values]
        with jsonlines.open(p, "w") as writer:  # type: ignore
            writer.write_all(values_dicts)  # type: ignore

    def _verify_header_len(self, header: Sequence[Any]) -> bool:
        """
        Ensures the passed header is the appropriate length given the Component's
        data_shape.

        Args:
            header (Sequence[Any]): A sequence of values to check.

        Raises:
            OutputError: If the length of header is less than the width of the
                Component's data.

        Returns:
            bool: True if the header passed verification.
        """
        if len(header) < self.data_shape[1]:
            raise OutputError(
                f"Supplied header length {len(header)} is insufficient for data "
                f"width {self.data_shape[1]}."
            )
        else:
            return True
