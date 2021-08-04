from __future__ import annotations

from typing import Any, Dict

from ..interfaces import BorderFormat, FullRange, Color
from ..dtypes import UserEnteredFmt, UserEnteredVal
from .. import _google_terms as terms


def add_alternating_row_background(
    tab_id: int, rng: FullRange, colors: Color
) -> Dict[str, Any]:
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{terms.TAB_ID: tab_id, **dict(rng)}],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{str(UserEnteredVal): "=MOD(ROW(), 2)"}],
                    },
                    "format": {"backgroundColor": dict(colors)},
                },
            },
            "index": rng.start_row,
        }
    }


def set_background_color(tab_id: int, rng: FullRange, color: Color):
    return {
        terms.RPT_CELL: {
            terms.RNG: {terms.TAB_ID: tab_id, **dict(rng)},
            terms.FIELDS: str(UserEnteredFmt),
            terms.CELL: {str(UserEnteredFmt): {"backgroundColor": dict(color)}},
        }
    }


def set_border_format(tab_id: int, rng: FullRange, *borders: BorderFormat):
    return {
        terms.RPT_CELL: {
            terms.RNG: {terms.TAB_ID: tab_id, **dict(rng)},
            terms.FIELDS: str(UserEnteredFmt),
            terms.CELL: {
                str(UserEnteredFmt): {
                    "borders": {**{k: v for b in borders for k, v in dict(b).items()}}
                }
            },
        }
    }
