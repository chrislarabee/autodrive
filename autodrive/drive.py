from typing import Dict, Any, Union
from pathlib import Path

from .connection import DriveConnection, DEFAULT_TOKEN, DEFAULT_CREDS


class Drive:
    def __init__(
        self,
        *,
        conn_config: Dict[str, Any] = None,
        token_filepath: Union[str, Path] = DEFAULT_TOKEN,
        creds_filepath: Union[str, Path] = DEFAULT_CREDS,
    ) -> None:
        self._conn = DriveConnection(
            secrets_config=conn_config,
            token_path=Path(token_filepath),
            creds_path=Path(creds_filepath),
        )
