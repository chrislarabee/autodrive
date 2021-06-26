import pytest

from autodrive.interfaces import RangeInterface, ParseRangeError, OneDRange, TwoDRange


class TestRangeInterface:
    def test_that_it_can_parse_range_strings(self):
        assert RangeInterface._parse_range_str("Sheet1!A1:C5") == ("Sheet1", "A1", "C5")
        assert RangeInterface._parse_range_str("A1:C50") == (None, "A1", "C50")
        assert RangeInterface._parse_range_str("A1:A") == (None, "A1", "A")
        assert RangeInterface._parse_range_str("A1") == (None, "A1", None)
        with pytest.raises(ParseRangeError, match="parb is not a valid range."):
            RangeInterface._parse_range_str("parb")

    def test_that_it_can_parse_cell_strings(self):
        assert RangeInterface._parse_cell_str("A1") == ("A", "1")
        assert RangeInterface._parse_cell_str("A") == ("A", None)

    def test_that_it_can_convert_cell_str_to_coordinate(self):
        assert RangeInterface._convert_cell_str_to_coord("A5") == (0, 4)
        assert RangeInterface._convert_cell_str_to_coord("AA") == (26, None)
        assert RangeInterface._convert_cell_str_to_coord("BC127") == (54, 126)

    def test_that_it_can_construct_range_strings(self):
        assert RangeInterface._construct_range_str(0, 6, 4, 10) == "E1:J6"
        assert RangeInterface._construct_range_str(0, 50) == "A1:A50"
        assert RangeInterface._construct_range_str(start_col=3, end_col=4) == "D1:D"
        assert RangeInterface._construct_range_str(end_row=50, end_col=5) == "A1:E50"

    def test_that_it_can_handle_alpha_to_idx_col_conversions(self):
        assert RangeInterface._convert_alpha_col_to_idx("A") == 0
        assert RangeInterface._convert_alpha_col_to_idx("AA") == 26
        assert RangeInterface._convert_alpha_col_to_idx("AB") == 27
        assert RangeInterface._convert_alpha_col_to_idx("AK") == 36
        assert RangeInterface._convert_alpha_col_to_idx("AZ") == 51
        assert RangeInterface._convert_alpha_col_to_idx("BA") == 52
        assert RangeInterface._convert_alpha_col_to_idx("ZA") == 676
        assert RangeInterface._convert_alpha_col_to_idx("AAA") == 702
        # Reverse conversions:
        assert RangeInterface._convert_col_idx_to_alpha(0) == "A"
        assert RangeInterface._convert_col_idx_to_alpha(26) == "AA"
        assert RangeInterface._convert_col_idx_to_alpha(27) == "AB"
        assert RangeInterface._convert_col_idx_to_alpha(36) == "AK"
        assert RangeInterface._convert_col_idx_to_alpha(51) == "AZ"
        assert RangeInterface._convert_col_idx_to_alpha(52) == "BA"
        assert RangeInterface._convert_col_idx_to_alpha(676) == "ZA"
        assert RangeInterface._convert_col_idx_to_alpha(702) == "AAA"


class TestOneDRange:
    def test_that_it_can_handle_str_idxs(self):
        result = OneDRange(0, "A", "C")
        assert result.start_idx == 0
        assert result.end_idx == 3

    def test_that_it_can_handle_zero_based_idxs(self):
        result = OneDRange(0, 0, 5, base0_idxs=True)
        assert result.start_idx == 0
        assert result.end_idx == 5
        result = OneDRange(0, 0, 5, base0_idxs=True, column=True)
        assert result.start_idx == 0
        assert result.end_idx == 5

    def test_that_it_can_handle_one_based_idxs(self):
        result = OneDRange(0, 1, 4)
        assert result.start_idx == 0
        assert result.end_idx == 5

    def test_that_it_can_convert_to_str(self):
        result = OneDRange(0, "A", "C")
        assert str(result) == "A1:C"


class TestTwoDRange:
    def test_that_it_can_handle_str_idxs_and_one_based_idxs(self):
        result = TwoDRange(0, 1, 50, "A", "K")
        assert result.start_row == 0
        assert result.end_row == 51
        assert result.start_col == 0
        assert result.end_col == 10

    def test_that_it_can_handle_str_idxs_and_zero_based_idxs(self):
        result = TwoDRange(0, 0, 51, "A", "K", base0_idxs=True)
        assert result.start_row == 0
        assert result.end_row == 51
        assert result.start_col == 0
        assert result.end_col == 10

    def test_that_it_can_handle_numeric_indxs(self):
        result = TwoDRange(0, 0, 51, 0, 11, base0_idxs=True)
        assert result.start_row == 0
        assert result.end_row == 51
        assert result.start_col == 0
        assert result.end_col == 11
        result = TwoDRange(0, 1, 50, 1, 10)
        assert result.start_row == 0
        assert result.end_row == 51
        assert result.start_col == 0
        assert result.end_col == 11

    def test_that_it_can_handle_range_str(self):
        result = TwoDRange(0, range_str="Sheet1!D5:E50")
        assert result.start_row == 4
        assert result.end_row == 50
        assert result.start_col == 3
        assert result.end_col == 5
        assert str(result) == "Sheet1!D5:E50"
        result = TwoDRange(0, range_str="D5:E")
        assert result.start_row == 4
        assert result.end_row is None
        assert result.start_col == 3
        assert result.end_col == 5
        assert str(result) == "D5:E"
        result = TwoDRange(0, range_str="D5")
        assert result.start_row == 0
        assert result.end_row == 5
        assert result.start_col == 0
        assert result.end_col == 4
        assert str(result) == "A1:D5"
