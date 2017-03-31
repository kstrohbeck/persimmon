import copy


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


class RewindIterator:
    def __init__(self, iterator):
        pass

    def __next__(self):
        pass

    def rewind_point(self):
        pass

    def rewind_to(self, point):
        pass

    def forget(self, point):
        pass
