from __future__ import annotations

from typing import Any, Dict

from ..interfaces import Format, TwoDRange, Color
from ..dtypes import UserEnteredVal
from ..core import Formatting


class CellFormatting(Formatting):
    pass


def add_alternating_row_background(rng: TwoDRange, colors: Color) -> Dict[str, Any]:
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [dict(rng)],
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
