from __future__ import annotations

from typing import Any, Dict

from .. import google_terms as terms


def auto_column_width(tab_id: int, start_col: int, end_col: int) -> Dict[str, Any]:
    return {
        "autoResizeDimensions": {
            terms.DIMS: {
                terms.TAB_ID: tab_id,
                terms.DIM: terms.COLDIM,
                terms.START_IDX: start_col,
                terms.END_IDX: end_col,
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
            "range": {
                terms.TAB_ID: tab_id,
                terms.DIM: terms.ROWDIM,
                terms.START_IDX: at_row,
                terms.END_IDX: at_row + num_rows,
            },
            "inheritFromBefore": False,
        }
    }


def delete_rows(tab_id: int, start_row: int, end_row: int) -> Dict[str, Any]:
    return {
        "deleteDimension": {
            terms.RNG: {
                terms.TAB_ID: tab_id,
                terms.DIM: terms.ROWDIM,
                terms.START_IDX: start_row,
                terms.END_IDX: end_row,
            }
        }
    }


def freeze(tab_id: int, rows: int = None, columns: int = None) -> Dict[str, Any]:
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
