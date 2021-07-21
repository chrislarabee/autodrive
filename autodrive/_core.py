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


class GoogleFormatType(type):
    """
    Metaclass for the three different ways format information is stored in
    Google Sheets.
    """

    format_key: str

    def __str__(cls) -> str:
        return cls.format_key
