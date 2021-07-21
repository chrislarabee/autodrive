from __future__ import annotations

from typing import Any, Dict

from ..interfaces import FullRange, Color
from ..dtypes import UserEnteredVal
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
