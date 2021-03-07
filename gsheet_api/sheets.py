from googleapiclient.discovery import Resource


class Sheets:
    def __init__(self, resource: Resource) -> None:
        self._core = resource
