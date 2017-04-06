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


expected = list(range(1, 10))


def test_rewind_iterator_wraps_inner_iterable(rewinder):
    assert list(rewinder) == expected


def test_rewind_rewinds_to_point(rewinder):
    with rewinder.rewind_point() as point:
        next(rewinder)
        rewinder.rewind_to(point)
        assert list(rewinder) == expected


def test_rewind_works_multiple_times(rewinder):
    with rewinder.rewind_point() as point:
        next(rewinder)
        rewinder.rewind_to(point)
        next(rewinder)
        rewinder.rewind_to(point)
        assert list(rewinder) == expected


def test_rewind_points_work_after_new_points_are_made(rewinder):
    with rewinder.rewind_point() as point:
        next(rewinder)
        with rewinder.rewind_point():
            next(rewinder)
            rewinder.rewind_to(point)
            assert list(rewinder) == expected


def test_rewind_points_work_after_other_points_are_forgotten(rewinder):
    point1 = rewinder.rewind_point()
    next(rewinder)
    point2 = rewinder.rewind_point()
    next(rewinder)
    rewinder.forget(point1)
    rewinder.rewind_to(point2)
    assert list(rewinder) == expected[1:]


def test_forgetting_point_doesnt_affect_index(rewinder):
    with rewinder.rewind_point() as point:
        next(rewinder)
        rewinder.rewind_to(point)
    assert list(rewinder) == expected


def test_earlier_points_are_less_than_later_points(rewinder):
    with rewinder.rewind_point() as point1:
        next(rewinder)
        with rewinder.rewind_point() as point2:
            assert point1 < point2


def test_same_points_are_equal(rewinder):
    with rewinder.rewind_point() as point1:
        next(rewinder)
        rewinder.rewind_to(point1)
        with rewinder.rewind_point() as point2:
            assert point1 == point2


def test_point_raises_if_eq_on_non_point(rewinder):
    with rewinder.rewind_point() as point:
        with pytest.raises(TypeError):
            assert point == 1


def test_point_raises_if_lt_on_non_point(rewinder):
    with rewinder.rewind_point() as point:
        with pytest.raises(TypeError):
            assert point < 1
