from typing import Any

class GoogleDtype(type):
    python_type: type
    type_key: str
    def __str__(cls: Any) -> str: ...
    @classmethod
    def parse(cls: Any, value: str) -> str: ...
