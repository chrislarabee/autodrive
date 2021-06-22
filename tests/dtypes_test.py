from autodrive.dtypes import (
    String,
    Number,
    Formula,
    Boolean,
    UserEnteredVal,
    FormattedVal,
)


class TestDtypes:
    def test_that_to_string_works(self):
        assert str(Number) == Number.type_key
        assert str(Boolean) == Boolean.type_key

    def test_that_they_can_parse_string_data(self):
        assert Number.parse("1.23") == 1.23
        assert Number.parse("123") == 123
        assert Boolean.parse("TRUE")
        assert not Boolean.parse("FALSE")
        assert String.parse("test") == "test"
        assert Formula.parse("=A1+A2") == "=A1+A2"


class TestGoogleValueTypes:
    def test_that_to_string_works(self):
        assert str(UserEnteredVal) == UserEnteredVal.value_key
        assert str(FormattedVal) == FormattedVal.value_key
