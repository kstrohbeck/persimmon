import pytest

from persimmon.utils import RewindIterator


def test_cant_next_abstract_rewind_iterator():
    with pytest.raises(NotImplementedError):
        rewinder = RewindIterator()
        next(rewinder)


def test_cant_get_index_of_abstract_rewind_iterator():
    with pytest.raises(NotImplementedError):
        rewinder = RewindIterator()
        assert rewinder.index


def test_cant_set_index_of_abstract_rewind_iterator():
    with pytest.raises(NotImplementedError):
        rewinder = RewindIterator()
        rewinder.index = 1
