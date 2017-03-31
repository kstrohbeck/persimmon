class Zipper:
    """List-like data structure that maintains a position, allowing for
    efficient lookup and modification at the cursor.
    """

    def __init__(self):
        """Create a new, empty zipper."""
        self._items = []
        self._index = 0

    def __len__(self):
        """Return the length of the zipper.

        :return: the zipper's length
        """
        return len(self._items)

    def __repr__(self):
        """Return a string representation of the zipper.

        :return: a string representation
        """
        def elem_str(index, elem):
            if index == self.index:
                return '<{}>'.format(repr(elem))
            else:
                return repr(elem)

        elem_strs = (elem_str(i, elem) for i, elem in enumerate(self._items))
        return '[{}]'.format(', '.join(elem_strs))

    @property
    def index(self):
        """The current index focused on by the zipper."""
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
        """
        return self._items[self.index]

    @property
    def is_at_end(self):
        """Indicates if the focus of the zipper is past all the elements.

        Trivially True if the zipper has no elements.

        :return: if the focus is at the end
        """
        return self.index == len(self)

    def append(self, value):
        """Append a value to the end of the zipper.

        :param value: the value to append
        """
        self._items.append(value)

    def advance(self):
        """Advance the focus to the right by 1.

        If the focus is at the end of the zipper, it won't move.
        """
        if not self.is_at_end:
            self.index += 1

    def delete_up_to(self, index):
        """Delete elements of the zipper up to the earliest of the given index,
        the focused index, and the end of the list.

        :param index: the index to delete to
        :return: the number of deleted elements
        """
        new_start = min(index, self.index)
        self._items = self._items[new_start]
        self.index -= new_start
        return new_start
