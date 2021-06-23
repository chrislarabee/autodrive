from __future__ import annotations

from typing import Any, Dict, overload

from .. import google_terms as terms
from ..interfaces import OneDRange


def auto_column_width(tab_id: int, start_col: int, end_col: int) -> Dict[str, Any]:
    return {
        "autoResizeDimensions": {
            terms.DIMS: {
                **dict(OneDRange(tab_id, start_col, end_col)),
                terms.DIM: terms.COLDIM,
            }
        }
    }


def append_rows(tab_id: int, num_rows: int) -> Dict[str, Any]:
    return {
        "appendDimension": {
            terms.TAB_ID: tab_id,
            terms.DIM: terms.ROWDIM,
            "length": num_rows,
        }
    }


def insert_rows(tab_id: int, num_rows: int, at_row: int) -> Dict[str, Any]:
    return {
        "insertDimension": {
            terms.RNG: {
                **dict(OneDRange(tab_id, at_row, at_row + num_rows)),
                terms.DIM: terms.ROWDIM,
            },
            "inheritFromBefore": False,
        }
    }


def delete_rows(tab_id: int, start_row: int, end_row: int) -> Dict[str, Any]:
    return {
        "deleteDimension": {
            terms.RNG: {
                **dict(OneDRange(tab_id, start_row, end_row)),
                terms.DIM: terms.ROWDIM,
            }
        }
    }


@overload
def freeze(tab_id: int, *, rows: int, columns: int = None) -> Dict[str, Any]:
    ...


@overload
def freeze(tab_id: int, *, columns: int, rows: int = None) -> Dict[str, Any]:
    ...


def freeze(tab_id: int, *, rows: int = None, columns: int = None) -> Dict[str, Any]:
    grid_prop = {}
    if not rows and not columns:
        raise ValueError("One of rows or columns must not be None.")
    if rows:
        grid_prop["frozenRowCount"] = rows
    if columns:
        grid_prop["frozenColumnCount"] = columns
    return {
        "updateSheetProperties": {
            terms.TAB_PROPS: {terms.TAB_ID: tab_id, terms.GRID_PROPS: grid_prop},
            terms.FIELDS: f"{terms.GRID_PROPS}(frozenRowCount, frozenColumnCount)",
        }
    }
