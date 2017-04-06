import pytest

from persimmon.utils import (
    StreamRewindIterator, StaticRewindIterator, BasicPosition, LinePosition
)


@pytest.fixture(params=[
    (StreamRewindIterator, range(1, 10)),
    (StaticRewindIterator, list(range(1, 10)))
])
def rewinder(request):
    cls, it = request.param
    return cls(it)


@pytest.fixture(params=[
    (StreamRewindIterator, range(1, 10)),
    (StaticRewindIterator, list(range(1, 10)))
])
def make_rewinder(request):
    cls, it = request.param
    return lambda pos: cls(it, pos)


@pytest.fixture(params=[BasicPosition, LinePosition])
def position(request):
    return request.param()
