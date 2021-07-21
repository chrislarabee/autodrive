import pytest

from autodrive.gsheet import GSheet
from autodrive.interfaces import (
    HalfRange,
    ParseRangeError,
    FullRange,
    _RangeInterface,
)
from autodrive import interfaces as intf
from autodrive.dtypes import FormattedVal


class TestRangeInterface:
    def test_that_it_can_parse_range_strings(self):
        assert _RangeInterface._parse_range_str("Sheet1!A1:C5") == (
            "Sheet1",
            "A1",
            "C5",
        )
        assert _RangeInterface._parse_range_str("A1:C50") == (None, "A1", "C50")
        assert _RangeInterface._parse_range_str("A1:A") == (None, "A1", "A")
        assert _RangeInterface._parse_range_str("A1") == (None, "A1", None)
        assert _RangeInterface._parse_range_str("A10:L10") == (None, "A10", "L10")
        with pytest.raises(  # type: ignore
            ParseRangeError, match="parb is not a valid range."
        ):
            _RangeInterface._parse_range_str("parb")

    def test_that_it_can_parse_cell_strings(self):
        assert _RangeInterface._parse_cell_str("A1") == ("A", "1")
        assert _RangeInterface._parse_cell_str("A") == ("A", None)

    def test_that_it_can_convert_cell_str_to_coordinate(self):
        assert _RangeInterface._convert_cell_str_to_coord("A5") == (0, 4)
        assert _RangeInterface._convert_cell_str_to_coord("AA") == (26, None)
        assert _RangeInterface._convert_cell_str_to_coord("BC127") == (54, 126)

    def test_that_it_can_construct_range_strings(self):
        assert _RangeInterface._construct_range_str() == "A1"
        assert _RangeInterface._construct_range_str(9, 20) == "U10"
        assert _RangeInterface._construct_range_str(0, 4, 5, 9) == "E1:J6"
        assert _RangeInterface._construct_range_str(0, end_row=49) == "A1:A50"
        assert _RangeInterface._construct_range_str(start_col=3, end_col=3) == "D1:D"
        assert _RangeInterface._construct_range_str(end_row=49, end_col=4) == "A1:E50"

    def test_that_it_can_handle_alpha_to_idx_col_conversions(self):
        assert _RangeInterface._convert_alpha_col_to_idx("A") == 0
        assert _RangeInterface._convert_alpha_col_to_idx("K") == 10
        assert _RangeInterface._convert_alpha_col_to_idx("AA") == 26
        assert _RangeInterface._convert_alpha_col_to_idx("AB") == 27
        assert _RangeInterface._convert_alpha_col_to_idx("AK") == 36
        assert _RangeInterface._convert_alpha_col_to_idx("AZ") == 51
        assert _RangeInterface._convert_alpha_col_to_idx("BA") == 52
        assert _RangeInterface._convert_alpha_col_to_idx("ZA") == 676
        assert _RangeInterface._convert_alpha_col_to_idx("AAA") == 702
        # Reverse conversions:
        assert _RangeInterface._convert_col_idx_to_alpha(0) == "A"
        assert _RangeInterface._convert_col_idx_to_alpha(26) == "AA"
        assert _RangeInterface._convert_col_idx_to_alpha(27) == "AB"
        assert _RangeInterface._convert_col_idx_to_alpha(36) == "AK"
        assert _RangeInterface._convert_col_idx_to_alpha(51) == "AZ"
        assert _RangeInterface._convert_col_idx_to_alpha(52) == "BA"
        assert _RangeInterface._convert_col_idx_to_alpha(676) == "ZA"
        assert _RangeInterface._convert_col_idx_to_alpha(702) == "AAA"

    def test_that_it_can_parse_idxs(self):
        assert _RangeInterface._parse_idx(10) == 9
        assert _RangeInterface._parse_idx(10, base0_idxs=True) == 10
        assert _RangeInterface._parse_idx("AA") == 26


class TestHalfRange:
    def test_that_it_can_handle_str_idxs(self):
        result = HalfRange("A", "C")
        assert result.start_idx == 0
        assert result.end_idx == 2
        assert result.column
        result = HalfRange(end_idx="C")
        assert result.start_idx == 0
        assert result.end_idx == 2
        assert result.column
        result = HalfRange(start_idx="A", end_idx="Z")
        assert result.start_idx == 0
        assert result.end_idx == 25
        assert result.column
        assert str(result) == "A1:Z"
        result = HalfRange(start_idx="A")
        assert result.start_idx == 0
        assert result.end_idx == 0
        assert result.column
        assert str(result) == "A1"

    def test_that_it_can_handle_zero_based_idxs(self):
        result = HalfRange(0, 5, base0_idxs=True)
        assert result.start_idx == 0
        assert result.end_idx == 5
        result = HalfRange(0, 5, base0_idxs=True, column=True)
        assert result.start_idx == 0
        assert result.end_idx == 5
        result = HalfRange(end_idx=9, base0_idxs=True)
        assert result.start_idx == 0
        assert result.end_idx == 9
        result = HalfRange(start_idx=19, base0_idxs=True)
        assert result.start_idx == 19
        assert result.end_idx == 19

    def test_that_it_can_handle_one_based_idxs(self):
        result = HalfRange(1, 4)
        assert result.start_idx == 0
        assert result.end_idx == 3
        assert dict(result) == {"startIndex": 0, "endIndex": 4}
        result = HalfRange(end_idx=10)
        assert result.start_idx == 0
        assert result.end_idx == 9
        result = HalfRange(start_idx=20)
        assert result.start_idx == 19
        assert result.end_idx == 19

    def test_that_it_can_convert_to_str(self):
        result = HalfRange("A", "C")
        assert result.start_idx == 0
        assert result.end_idx == 2
        assert str(result) == "A1:C"


class TestFullRange:
    def test_that_it_can_handle_str_idxs_and_one_based_idxs(self):
        result = FullRange(start_row=1, end_row=50, start_col="A", end_col="K")
        assert result.start_row == 0
        assert result.end_row == 49
        assert result.start_col == 0
        assert result.end_col == 10
        assert str(result) == "A1:K50"
        result = FullRange(start_row=5, start_col="B")
        assert result.start_row == 4
        assert result.start_col == 1
        assert result.end_row == 4
        assert result.end_col == 1
        assert str(result) == "B5"
        result = FullRange(start_col="A", end_col="B", end_row=50)
        assert result.start_row == 0
        assert result.start_col == 0
        assert result.end_col == 1
        assert result.end_row == 49
        assert str(result) == "A1:B50"

    def test_that_it_can_handle_str_idxs_and_zero_based_idxs(self):
        result = FullRange(
            start_row=0, end_row=49, start_col="A", end_col="K", base0_idxs=True
        )
        assert result.start_row == 0
        assert result.end_row == 49
        assert result.start_col == 0
        assert result.end_col == 10
        assert str(result) == "A1:K50"
        result = FullRange(start_row=4, start_col="B", base0_idxs=True)
        assert result.start_row == 4
        assert result.start_col == 1
        assert result.end_row == 4
        assert result.end_col == 1
        assert str(result) == "B5"
        result = FullRange(end_row=50, end_col="K")
        assert result.start_row == 0
        assert result.start_col == 0
        assert result.end_row == 49
        assert result.end_col == 10
        assert str(result) == "A1:K50"
        result = FullRange(start_col="A", end_col="B", end_row=49, base0_idxs=True)
        assert result.start_row == 0
        assert result.start_col == 0
        assert result.end_col == 1
        assert result.end_row == 49
        assert str(result) == "A1:B50"

    def test_that_it_can_handle_zero_based_numeric_idxs(self):
        result = FullRange(
            start_row=0, end_row=49, start_col=0, end_col=10, base0_idxs=True
        )
        assert result.start_row == 0
        assert result.end_row == 49
        assert result.start_col == 0
        assert result.end_col == 10
        assert str(result) == "A1:K50"
        result = FullRange(start_row=4, start_col=1, base0_idxs=True)
        assert result.start_row == 4
        assert result.start_col == 1
        assert result.end_row == 4
        assert result.end_col == 1
        assert str(result) == "B5"
        result = FullRange(end_row=49, end_col=10, base0_idxs=True)
        assert result.start_row == 0
        assert result.start_col == 0
        assert result.end_row == 49
        assert result.end_col == 10
        assert str(result) == "A1:K50"
        result = FullRange(start_col=0, end_col=1, end_row=49, base0_idxs=True)
        assert result.start_row == 0
        assert result.start_col == 0
        assert result.end_col == 1
        assert result.end_row == 49
        assert str(result) == "A1:B50"

    def test_that_it_can_handle_one_based_numeric_idxs(self):
        result = FullRange(start_row=1, end_row=50, start_col=1, end_col=11)
        assert result.start_row == 0
        assert result.end_row == 49
        assert result.start_col == 0
        assert result.end_col == 10
        assert str(result) == "A1:K50"
        result = FullRange(start_row=5, start_col=2)
        assert result.start_row == 4
        assert result.start_col == 1
        assert result.end_row == 4
        assert result.end_col == 1
        assert str(result) == "B5"
        result = FullRange(end_row=50, end_col=11)
        assert result.start_row == 0
        assert result.start_col == 0
        assert result.end_row == 49
        assert result.end_col == 10
        assert str(result) == "A1:K50"
        result = FullRange(start_col=1, end_col=2, end_row=50)
        assert result.start_row == 0
        assert result.start_col == 0
        assert result.end_col == 1
        assert result.end_row == 49
        assert str(result) == "A1:B50"

    def test_that_it_can_handle_range_str(self):
        result = FullRange("Sheet1!D5:E50")
        assert result.start_row == 4
        assert result.end_row == 49
        assert result.start_col == 3
        assert result.end_col == 4
        assert str(result) == "Sheet1!D5:E50"
        result = FullRange("D5:E")
        assert result.start_row == 4
        assert result.end_row is None
        assert result.start_col == 3
        assert result.end_col == 4
        assert str(result) == "D5:E"
        result = FullRange("D5")
        assert result.start_row == 4
        assert result.end_row == 5
        assert result.start_col == 3
        assert result.end_col == 4
        assert str(result) == "D5"
        result = FullRange("A10:L10")
        assert result.start_row == 9
        assert result.end_row == 9
        assert result.start_col == 0
        assert result.end_col == 11
        with pytest.raises(ParseRangeError):  # type: ignore
            FullRange("D:D50")


class TestColor:
    def test_that_it_can_handle_odd_inputs(self):
        pass


@pytest.mark.connection
def test_that_all_numeric_formats_work_as_expected(test_gsheet: GSheet):
    # This is partially to act as a safeguard against google changing the
    # pattern representations of these formats, so think twice before deleting:
    tab = test_gsheet.tabs["Sheet1"]
    rng = FullRange("A10:L10")
    tab.write_values([[1234.56 for _ in range(12)]], rng)
    formats = [
        (intf.AutomaticFormat, "1234.56"),
        (intf.NumberFormat, "1,234.56"),
        (intf.AccountingFormat, " $ 1,234.56 "),
        (intf.PercentFormat, "123456.00%"),
        (intf.ScientificFormat, "1.23E+03"),
        (intf.FinancialFormat, "1,234.56"),
        (intf.CurrencyFormat, "$1,234.56"),
        (intf.CurRoundFormat, "$1,235"),
        (intf.DateFormat, "5/18/1903"),
        (intf.TimeFormat, "1:26:24 PM"),
        (intf.DatetimeFormat, "5/18/1903 13:26:24"),
        (intf.DurationFormat, "29629:26:24"),
    ]
    for i, fmt in enumerate(formats, 1):
        tab.format_text.apply_format(
            fmt[0], FullRange(start_row=10, start_col=i, end_col=i)
        )
    tab.commit()
    tab.get_data(rng, FormattedVal)
    for i, fmt in enumerate(formats):
        pattern = tab.formats[0][i]["numberFormat"].get("pattern", "")
        value = tab.values[0][i]
        assert pattern == fmt[0].pattern
        assert value == fmt[1]
