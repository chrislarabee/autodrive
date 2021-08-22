class GoogleDtype(type):
    """
    Metaclass for the four data types used in Google Sheets.
    """

    python_type: type
    type_key: str

    def __str__(cls) -> str:
        return cls.type_key

    @classmethod
    def parse(cls, value: str) -> str:
        return cls.python_type(value)
