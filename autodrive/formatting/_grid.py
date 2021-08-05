from __future__ import annotations

from typing import Any, Dict, overload

from .. import _google_terms as terms
from ..interfaces import HalfRange


def auto_column_width(tab_id: int, rng: HalfRange) -> Dict[str, Any]:
    return {
        "autoResizeDimensions": {
            terms.DIMS: {
                terms.TAB_ID: tab_id,
                **dict(rng),
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
                terms.TAB_ID: tab_id,
                **dict(HalfRange(at_row, at_row + num_rows, base0_idxs=True)),
                terms.DIM: terms.ROWDIM,
            },
            "inheritFromBefore": False,
        }
    }


def delete_rows(tab_id: int, rng: HalfRange) -> Dict[str, Any]:
    return {
        "deleteDimension": {
            terms.RNG: {
                terms.TAB_ID: tab_id,
                **dict(rng),
                terms.DIM: terms.ROWDIM,
            }
        }
    }


@overload
def freeze(tab_id: int, *, rows: int, columns: int | None = None) -> Dict[str, Any]:
    ...


@overload
def freeze(tab_id: int, *, columns: int, rows: int | None = None) -> Dict[str, Any]:
    ...


def freeze(
    tab_id: int, *, rows: int | None = None, columns: int | None = None
) -> Dict[str, Any]:
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


def append_columns(tab_id: int, num_cols: int) -> Dict[str, Any]:
    return {
        "appendDimension": {
            terms.TAB_ID: tab_id,
            terms.DIM: terms.COLDIM,
            "length": num_cols,
        }
    }


def insert_columns(tab_id: int, num_cols: int, at_col: int) -> Dict[str, Any]:
    return {
        "insertDimension": {
            terms.RNG: {
                terms.TAB_ID: tab_id,
                **dict(HalfRange(at_col, at_col + num_cols, base0_idxs=True)),
                terms.DIM: terms.COLDIM,
            },
            "inheritFromBefore": False,
        }
    }


def delete_columns(tab_id: int, rng: HalfRange) -> Dict[str, Any]:
    return {
        "deleteDimension": {
            terms.RNG: {
                terms.TAB_ID: tab_id,
                **dict(rng),
                terms.DIM: terms.COLDIM,
            }
        }
    }
