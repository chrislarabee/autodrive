import pytest

from autodrive.range import Range, ParseRangeError


class TestRange:
    def test_that_it_instantiates_properly(self):
        rng = Range(
            "Sheet1!D5:E50",
            tab_title="test",
            gsheet_id="test",
            tab_id=0,
            autoconnect=False,
        )
        assert rng.start_row_idx == 4
        assert rng.end_row_idx == 50
        assert rng.start_col_idx == 3
        assert rng.end_col_idx == 5
        assert rng.range_str == "Sheet1!D5:E50"
        assert str(rng) == "Sheet1!D5:E50"
        rng = Range(
            "D5:E", tab_title="test", gsheet_id="test", tab_id=0, autoconnect=False
        )
        assert rng.start_row_idx == 4
        assert rng.end_row_idx is None
        assert rng.start_col_idx == 3
        assert rng.end_col_idx == 5
        assert rng.range_str == "test!D5:E"

    def test_that_it_can_parse_range_strings(self):
        assert Range._parse_range_str("Sheet1!A1:C5") == ("Sheet1", "A1", "C5")
        assert Range._parse_range_str("A1:C50") == (None, "A1", "C50")
        assert Range._parse_range_str("A1:A") == (None, "A1", "A")
        assert Range._parse_range_str("A1") == (None, "A1", None)
        with pytest.raises(ParseRangeError, match="parb is not a valid range."):
            Range._parse_range_str("parb")

    def test_that_it_can_parse_cell_strings(self):
        assert Range._parse_cell_str("A1") == ("A", "1")
        assert Range._parse_cell_str("A") == ("A", None)

    def test_that_it_can_convert_cell_str_to_coordinate(self):
        assert Range._convert_cell_str_to_coord("A5") == (0, 4)
        assert Range._convert_cell_str_to_coord("AA") == (26, None)
        assert Range._convert_cell_str_to_coord("BC127") == (54, 126)

    def test_that_it_can_construct_range_strings(self):
        assert Range._construct_range_str("Sheet1") == "Sheet1"
        assert Range._construct_range_str("Sheet1", (0, 5), (4, 9)) == "Sheet1!E1:J6"

    def test_that_it_can_handle_alpha_to_idx_col_conversions(self):
        assert Range._convert_alpha_col_to_idx("A") == 0
        assert Range._convert_alpha_col_to_idx("AA") == 26
        assert Range._convert_alpha_col_to_idx("AB") == 27
        assert Range._convert_alpha_col_to_idx("AK") == 36
        assert Range._convert_alpha_col_to_idx("AZ") == 51
        assert Range._convert_alpha_col_to_idx("BA") == 52
        assert Range._convert_alpha_col_to_idx("ZA") == 676
        assert Range._convert_alpha_col_to_idx("AAA") == 702
        # Reverse conversions:
        assert Range._convert_col_idx_to_alpha(0) == "A"
        assert Range._convert_col_idx_to_alpha(26) == "AA"
        assert Range._convert_col_idx_to_alpha(27) == "AB"
        assert Range._convert_col_idx_to_alpha(36) == "AK"
        assert Range._convert_col_idx_to_alpha(51) == "AZ"
        assert Range._convert_col_idx_to_alpha(52) == "BA"
        assert Range._convert_col_idx_to_alpha(676) == "ZA"
        assert Range._convert_col_idx_to_alpha(702) == "AAA"
