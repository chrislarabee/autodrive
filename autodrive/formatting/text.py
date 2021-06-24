from __future__ import annotations

from typing import Dict, Any

from ..interfaces import TwoDRange, TextFormat
from .. import google_terms as terms


def apply_format(rng: TwoDRange, fmt: TextFormat) -> Dict[str, Any]:
    return {
        terms.RPT_CELL: {
            terms.RNG: dict(rng),
            terms.FIELDS: str(fmt),
            terms.CELL: dict(fmt),
        }
    }
