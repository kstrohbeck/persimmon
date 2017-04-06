import pytest

from persimmon.utils import Position, BasicPosition, LinePosition


def parametrize_line_position():
    return pytest.mark.parametrize(['line', 'col'], [
        (1, 0),
        (0, 1),
        (100, 100)
    ])


def parametrize_basic_position():
    return pytest.mark.parametrize('index', [0, 1, 2, 10, 1000])


def test_abstract_position_shift_raises():
    pos = Position()
    with pytest.raises(NotImplementedError):
        pos.shift(None)


def test_abstract_position_value_raises():
    pos = Position()
    with pytest.raises(NotImplementedError):
        _ = pos.value


@parametrize_basic_position()
def test_basic_pos_value_is_index(index):
    pos = BasicPosition(index)
    assert pos.value == index


@parametrize_line_position()
def test_line_pos_value_is_line_and_col(line, col):
    pos = LinePosition(line, col)
    assert pos.value == (line, col)


@parametrize_basic_position()
def test_basic_pos_shift_increases_by_one(index):
    pos = BasicPosition(index)
    assert pos.shift(None).value == index + 1


@parametrize_line_position()
def test_line_pos_shift_doesnt_affect_line_on_non_newline(line, col):
    pos = LinePosition(line, col)
    assert pos.shift(None).value[0] == line


@parametrize_line_position()
def test_line_pos_shift_increases_col_by_one_on_non_newline(line, col):
    pos = LinePosition(line, col)
    assert pos.shift(None).value[1] == col + 1


@parametrize_line_position()
def test_line_pos_shift_increases_line_by_one_on_newline(line, col):
    pos = LinePosition(line, col)
    assert pos.shift('\n').value[0] == line + 1


@parametrize_line_position()
def test_line_pos_shift_sets_col_to_zero_on_newline(line, col):
    pos = LinePosition(line, col)
    assert pos.shift('\n').value[1] == 0


@parametrize_basic_position()
def test_basic_pos_repr_is_index(index):
    pos = BasicPosition(index)
    assert repr(pos) == repr(index)


@pytest.mark.parametrize(['line', 'col', 'expected'], [
    (1, 0, 'line 1, column 0'),
    (0, 1, 'line 0, column 1'),
    (100, 100, 'line 100, column 100')
])
def test_line_pos_repr_is_line_and_column(line, col, expected):
    pos = LinePosition(line, col)
    assert repr(pos) == expected
