import pytest

from persimmon.utils import StreamRewindIterator, StaticRewindIterator


@pytest.fixture(params=[
    (StreamRewindIterator, range(1, 10)),
    (StaticRewindIterator, list(range(1, 10)))
])
def rewinder(request):
    cls, it = request.param
    return cls(it)


