import pytest

from lib.schema import Column, Schema


class TestColumn:
    def test__init__(self):
        with pytest.raises(ValueError):
            c = Column(dtype='junk')

        with pytest.raises(ValueError):
            c = Column(dtype=int, default='junk')


class TestSchema:
    def test_bool(self):
        assert not Schema._bool('FALSE')
        assert Schema._bool('TRUE')

        with pytest.raises(ValueError):
            Schema._bool('junk')

    def test_convert(self):
        assert Schema._convert('1.2', float) == 1.2
        assert Schema._convert('65', int) == 65
        assert Schema._convert('TRUE', bool)
        assert Schema._convert('1.2', 'any') == 1.2
        assert Schema._convert('65', 'any') == 65
        assert not Schema._convert('FALSE', 'any')

    def test_parse(self):
        s = Schema(
            colA=None,
            colB=int,
            colC=(float, 5.5)
        )

        row_data = {'colA': 'value', 'colB': '120', 'colC': '6.2'}
        expected = {'colA': 'value', 'colB': 120, 'colC': 6.2}

        assert s.parse(row_data) == expected

    def test_parse_defaults(self):
        s = Schema(
            colA=(str, 'placeholder'),
            colB=int,
            colC=(float, 5.5)
        )

        row_data = {'colA': 'value'}
        expected = {'colA': 'value', 'colB': None, 'colC': 5.5}

        assert s.parse(row_data) == expected
