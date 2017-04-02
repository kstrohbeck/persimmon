import collections
import copy
import functools


class Zipper:
    """List-like data structure that maintains a position, allowing for
    efficient lookup and modification at the cursor.
    """

    def __init__(self):
        """Create a new, empty zipper.

        >>> zipper = Zipper()
        >>> zipper
        []
        """
        self._items = []
        self._index = 0

    def __len__(self):
        """Return the length of the zipper.

        :return: the zipper's length

        >>> zipper = Zipper()
        >>> len(zipper)
        0
        >>> zipper.append(1)
        >>> len(zipper)
        1
        """
        return len(self._items)

    def __repr__(self):
        """Return a string representation of the zipper.

        :return: a string representation

        >>> zipper = Zipper.from_list([1, 2, 3])
        >>> repr(zipper)
        '[<1>, 2, 3]'
        """
        def elem_str(index, elem):
            if index == self.index:
                return '<{}>'.format(repr(elem))
            else:
                return repr(elem)

        elem_strs = (elem_str(i, elem) for i, elem in enumerate(self._items))
        return '[{}]'.format(', '.join(elem_strs))

    def __eq__(self, other):
        """Returns if this zipper is equal to another object.

        Zippers are equal if their contents are the same, and their focus is
        on the same object.

        :param other: the object to check equality against
        :return: whether the zipper and other object are equal

        >>> zipper = Zipper()
        >>> zipper == Zipper()
        True
        >>> zipper == Zipper.from_list([1])
        False
        >>> Zipper.from_list([1, 2, 3], 1) == Zipper.from_list([1, 2, 3], 2)
        False
        """
        if not isinstance(other, Zipper):
            return False

        return self._items == other._items and self._index == other._index

    @property
    def index(self):
        """The current index focused on by the zipper.

        :return: the current index

        >>> zipper = Zipper.from_list([1, 2, 3])
        >>> zipper.index
        0
        >>> zipper.advance()
        >>> zipper.index
        1
        """
        return self._index

    @index.setter
    def index(self, new_index):
        if new_index > len(self):
            raise IndexError
        self._index = new_index

    @property
    def cur_item(self):
        """Return the item focused on by the zipper.

        If there isn't a focused element (because the zipper has zero length),
        this method will raise an IndexError.

        :return: the current item

        >>> zipper = Zipper.from_list([1, 2, 3])
        >>> zipper.cur_item
        1
        >>> zipper.advance()
        >>> zipper.cur_item
        2
        """
        return self._items[self.index]

    @property
    def is_at_end(self):
        """Indicates if the focus of the zipper is past all the elements.

        Trivially True if the zipper has no elements.

        :return: if the focus is at the end

        >>> zipper = Zipper.from_list([1, 2, 3])
        >>> zipper.is_at_end
        False
        >>> zipper.index = 3
        >>> zipper.is_at_end
        True
        """
        return self.index == len(self)

    @classmethod
    def from_list(cls, items, index=0):
        """Creates a zipper from a list with an optional index value.

        :param items: the list of items to turn into a zipper
        :param index: the index of the zipper; defaults to 0.
        :return: the created zipper

        >>> Zipper.from_list([1, 2, 3])
        [<1>, 2, 3]
        """
        zipper = cls()
        zipper._items = copy.copy(items)
        zipper.index = index
        return zipper

    def append(self, value):
        """Append a value to the end of the zipper.

        :param value: the value to append

        >>> zipper = Zipper()
        >>> zipper
        []
        >>> zipper.append(1)
        >>> zipper
        [<1>]
        >>> zipper.append(2)
        >>> zipper
        [<1>, 2]
        """
        self._items.append(value)

    def advance(self):
        """Advance the focus to the right by 1.

        If the focus is at the end of the zipper, it won't move.

        >>> zipper = Zipper.from_list([1, 2, 3])
        >>> zipper
        [<1>, 2, 3]
        >>> zipper.advance()
        >>> zipper
        [1, <2>, 3]
        """
        if not self.is_at_end:
            self.index += 1

    def delete_up_to(self, index):
        """Delete elements of the zipper up to the earliest of the given index,
        the focused index, and the end of the list, returning how many elements
        were deleted.

        :param index: the index to delete to
        :return: the number of deleted elements

        >>> zipper = Zipper.from_list([1, 2, 3])
        >>> zipper.index = 2
        >>> zipper
        [1, 2, <3>]
        >>> zipper.delete_up_to(1)
        1
        >>> zipper
        [2, <3>]
        """
        new_start = min(index, self.index)
        self._items = self._items[new_start:]
        self.index -= new_start
        return new_start


@functools.total_ordering
class RewindPoint:
    """Represents a point that a specific RewindIterator can be rewound to."""

    def __init__(self, rewinder, index):
        """Create a new rewind point.

        :param rewinder: the rewinder this point belongs to
        :param index: the index of the rewind point
        """
        self._rewinder = rewinder
        self.index = index

    def __enter__(self):
        """Called when the rewind point is created in a with statement.

        :return: this point
        """
        return self

    def __exit__(self, *_):
        """Called when the rewind point exits the with statement it was created
        in.
        """
        self._rewinder.forget(self)

    def __eq__(self, other):
        if not isinstance(other, RewindPoint):
            raise TypeError

        return self._rewinder == other._rewinder and self.index == other.index

    def __lt__(self, other):
        """Indicates if this point occurred earlier than the other point.

        Raises a TypeError if other is not a RewindPoint.

        :param other: the other rewind point
        :return: if this point is earlier than the other
        """
        if not isinstance(other, RewindPoint):
            raise TypeError

        return self._rewinder == other._rewinder and self.index < other.index


class RewindIterator(collections.Iterator):
    """Wrapper around some backing type that provides standard iterator features
    as well as allowing for setting and deleting backtracking points.
    """

    def __init__(self):
        """Create a new rewind iterator."""
        self._points = []

    def __next__(self):
        """Return the next element of the backing data."""
        raise NotImplementedError

    @property
    def index(self):
        """The current index in the data."""
        raise NotImplementedError

    @index.setter
    def index(self, index):
        raise NotImplementedError

    def rewind_point(self):
        """Create a new rewind point at the current index.

        The point can be used to rewind the iterator to the state it was at when
        the point was created.

        :return: the rewind point
        """
        point = RewindPoint(self, self.index)
        self._points.append(point)
        return point

    def rewind_to(self, point):
        """Rewind the iterator to the given point.

        :param point: the point to rewind to
        :return:
        """
        self.index = point.index

    def forget(self, point):
        """Forget a point.

        Once a point is forgotten, it can no longer be rewound to. Forgetting a
        point does not affect any other points, even points recorded before it
        or at the same time.

        :param point: the point to forget
        """
        self._points.remove(point)

    @staticmethod
    def make_rewind_iterator(data):
        """Create a new rewind iterator, specializing it based on the type of
        the data.

        For efficiency, a static rewind iterator is used, but it only works if
        the data supports indexing (has the __getitem__ method defined.)
        Iterables and iterators are made into a stream rewinder. Other values
        are not supported.

        :param data: the data to wrap
        :return: the rewind iterator
        """
        if hasattr(data, '__getitem__'):
            return StaticRewindIterator(data)
        elif hasattr(data, '__iter__'):
            return StreamRewindIterator(data)
        # TODO: customize exception
        raise Exception


class StreamRewindIterator(RewindIterator):
    """Wrapper around an iterable/iterator that allows backtracking.

    This iterator attempts to preserve as little data as possible. It guarantees
    the validity of a rewind point for that point's entire lifetime, but data
    before the first rewind point can be deleted at any time.
    """

    def __init__(self, iterable):
        """Create a new stream rewind iterator.

        The iterable has to support either __iter__ or __next__.

        :param iterable: the iterable stream to wrap
        """
        super().__init__()
        self._iterator = iter(iterable)
        self._store = Zipper()

    def __next__(self):
        if self._store.is_at_end:
            value = next(self._iterator)
            if not self._points:
                return value
            self._store.append(value)
        else:
            value = self._store.cur_item
        self._store.advance()
        if not self._points and self._store.is_at_end:
            self._store = Zipper()
        return value

    @property
    def index(self):
        return self._store.index

    @index.setter
    def index(self, index):
        self._store.index = index

    def forget(self, point):
        super().forget(point)
        if self._points and point.index == 0:
            earliest = None
            for point in self._points:
                if earliest is None or point.index < earliest.index:
                    earliest = point
            new_start = self._store.delete_up_to(earliest.index)
            for point in self._points:
                point.index -= new_start


class StaticRewindIterator(RewindIterator):
    """Wrapper around a static store of data that allows backtracking.

    The wrapper does not mutate the backing data. This means that it won't
    delete any elements, but rewinding past the first recording point is not
    supported.
    """

    def __init__(self, data):
        """Creates a new static rewind iterator.

        data must be indexable - it has to have __getitem__ defined.

        :param data: the data to iterate over
        """
        super().__init__()
        self._data = data
        self._index = 0

    def __next__(self):
        if self._index >= len(self._data):
            raise StopIteration
        value = self._data[self._index]
        self._index += 1
        return value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index
