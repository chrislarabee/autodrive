from typing import List, Any, Dict
from pathlib import Path
import csv
import jsonlines  # type: ignore

import pytest

from autodrive.gsheet import GSheet
from autodrive.tab import Tab
from autodrive._view import OutputError


def read_csv(p: Path) -> List[List[Any]]:
    result: List[List[Any]] = []
    with open(p, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            result.append(row)
    return result


def read_jsonl(p: Path) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    with jsonlines.open(p, "r") as reader:  # type: ignore
        for row in reader:  # type: ignore
            result.append(row)  # type: ignore
    return result


sample_tabs: List[Tab] = []
for i in range(3):
    tab = Tab("test", f"test{i + 1}", i, i)
    tab.values = [[1 + i, 2 + i, 3 + i], [4 + i, 5 + i, 6 + i]]
    sample_tabs.append(tab)

sample_gsheet = GSheet("test", "test", autoconnect=False, tabs=sample_tabs)
root_path = Path("tests")


class TestValuesOutput:
    def test_that_components_can_output_csv(self):
        tab = Tab("test", "test", 0, 0, autoconnect=False)
        tab.values = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        p = Path("tests/example.csv")
        tab.to_csv(p)
        expected = [["A", "B", "C"], ["1", "2", "3"], ["4", "5", "6"]]
        result = read_csv(p)
        assert result == expected
        tab.values = [[1, 2, 3], [4, 5, 6]]
        tab.to_csv(p, ["A", "B", "C"])
        result = read_csv(p)
        assert result == expected
        with pytest.raises(  # type: ignore
            OutputError, match="header length 2 is insufficient"
        ):
            tab.to_csv(p, ["A", "B"])
        p.unlink()

    def test_that_components_can_output_json(self):
        tab = Tab("test", "test", 0, 0, autoconnect=False)
        tab.values = [["A", "B", "C"], [1, 2, 3], [4, 5, 6]]
        p = Path("tests/example.jsonl")
        tab.to_json(p, 0)
        expected: List[Dict[str, int]] = [dict(A=1, B=2, C=3), dict(A=4, B=5, C=6)]
        result = read_jsonl(p)
        assert result == expected
        tab.values = [[1, 2, 3], [4, 5, 6]]
        tab.to_json(p, ["A", "B", "C"])
        result = read_jsonl(p)
        assert result == expected
        with pytest.raises(  # type: ignore
            OutputError, match="header length 2 is insufficient"
        ):
            tab.to_json(p, ["A", "B"])
        p.unlink()

    def test_that_gsheet_can_output_tabs_to_csv(self):
        sample_gsheet.to_csv(
            root_path,
            filename_overrides={"test2": "test_duo.csv"},
            test1=["A", "B", "C"],
            test2=None,
        )
        p1 = root_path.joinpath("test1.csv")
        result1 = read_csv(p1)
        expected = [["A", "B", "C"], ["1", "2", "3"], ["4", "5", "6"]]
        assert result1 == expected
        p2 = root_path.joinpath("test_duo.csv")
        assert p2.exists()
        result2 = read_csv(p2)
        expected = [["2", "3", "4"], ["5", "6", "7"]]
        assert result2 == expected
        assert not root_path.joinpath("test3.csv").exists()
        p1.unlink()
        p2.unlink()

    def test_that_gsheet_can_output_tabs_to_json(self):
        sample_gsheet.to_json(
            root_path,
            filename_overrides={"test2": "test_duo.jsonl"},
            test1=["A", "B", "C"],
            test2=0,
        )
        p1 = root_path.joinpath("test1.jsonl")
        result1 = read_jsonl(p1)
        expected: List[Dict[str, int]] = [dict(A=1, B=2, C=3), dict(A=4, B=5, C=6)]
        assert result1 == expected
        p2 = root_path.joinpath("test_duo.jsonl")
        assert p2.exists()
        result2 = read_jsonl(p2)
        expected = [{"2": 5, "3": 6, "4": 7}]
        assert result2 == expected
        assert not root_path.joinpath("test3.jsonl").exists()
        p1.unlink()
        p2.unlink()

    def test_that_gsheet_can_output_all_tabs_to_csv_with_defaults(self):
        overrides = {"test1": "test_a", "test2": "test_b", "test3": "test_c"}
        sample_gsheet.to_csv(root_path, filename_overrides=overrides)
        for file_name in overrides.values():
            p = root_path.joinpath(file_name).with_suffix(".csv")
            assert p.exists()
            p.unlink()

    def test_that_gsheet_can_output_all_tabs_to_json_with_defaults(self):
        overrides = {"test1": "test_a", "test2": "test_b", "test3": "test_c"}
        sample_gsheet.to_json(root_path, filename_overrides=overrides)
        for file_name in overrides.values():
            p = root_path.joinpath(file_name).with_suffix(".jsonl")
            assert p.exists()
            p.unlink()
