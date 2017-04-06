import pytest

from persimmon.utils import StreamRewindIterator


class TestRewindIterator:
    def test_rewind_iterator_wraps_inner_iterable(self):
        iterable = range(1, 10)
        rewinder = StreamRewindIterator(iterable)
        assert list(rewinder) == list(range(1, 10))

    def test_rewind_rewinds_to_point(self):
        rewinder = StreamRewindIterator(range(1, 10))
        with rewinder.rewind_point() as point:
            next(rewinder)
            rewinder.rewind_to(point)
            assert list(rewinder) == list(range(1, 10))

    def test_rewind_works_multiple_times(self):
        rewinder = StreamRewindIterator(range(1, 10))
        with rewinder.rewind_point() as point:
            next(rewinder)
            rewinder.rewind_to(point)
            next(rewinder)
            rewinder.rewind_to(point)
            assert list(rewinder) == list(range(1, 10))

    def test_rewind_points_work_after_new_points_are_made(self):
        rewinder = StreamRewindIterator(range(1, 10))
        with rewinder.rewind_point() as point:
            next(rewinder)
            with rewinder.rewind_point():
                next(rewinder)
                rewinder.rewind_to(point)
                assert list(rewinder) == list(range(1, 10))

    def test_rewind_points_work_after_other_points_are_forgotten(self):
        rewinder = StreamRewindIterator(range(1, 10))
        point1 = rewinder.rewind_point()
        next(rewinder)
        point2 = rewinder.rewind_point()
        next(rewinder)
        rewinder.forget(point1)
        rewinder.rewind_to(point2)
        assert list(rewinder) == list(range(2, 10))

    def test_forgetting_point_doesnt_affect_index(self):
        rewinder = StreamRewindIterator(range(1, 10))
        with rewinder.rewind_point() as point:
            next(rewinder)
            rewinder.rewind_to(point)
        assert list(rewinder) == list(range(1, 10))

    def test_earlier_points_are_less_than_later_points(self):
        rewinder = StreamRewindIterator(range(1, 10))
        with rewinder.rewind_point() as point1:
            next(rewinder)
            with rewinder.rewind_point() as point2:
                assert point1 < point2

    def test_same_points_are_equal(self):
        rewinder = StreamRewindIterator(range(1, 10))
        with rewinder.rewind_point() as point1:
            next(rewinder)
            rewinder.rewind_to(point1)
            with rewinder.rewind_point() as point2:
                assert point1 == point2

    def test_point_raises_if_eq_on_non_point(self):
        rewinder = StreamRewindIterator(range(1, 10))
        with rewinder.rewind_point() as point:
            with pytest.raises(TypeError):
                assert point == 1

    def test_point_raises_if_lt_on_non_point(self):
        rewinder = StreamRewindIterator(range(1, 10))
        with rewinder.rewind_point() as point:
            with pytest.raises(TypeError):
                assert point < 1
