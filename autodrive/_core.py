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


class GoogleValueType(type):
    """
    Metaclass for the three different ways values are stored in Google Sheets.
    """

    value_key: str
    has_dtype: bool = True

    def __str__(cls) -> str:
        return cls.value_key


class GoogleFormatType(type):
    """
    Metaclass for the three different ways format information is stored in
    Google Sheets.
    """

    format_key: str

    def __str__(cls) -> str:
        return cls.format_key
