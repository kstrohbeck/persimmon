class Zipper:
    """List-like data structure that maintains a position, allowing for
    efficient lookup and modification at the cursor.
    """

    def __init__(self):
        """Create a new, empty zipper."""
        self._items = []
        self.index = 0

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
    def cur_item(self):
        """Return the item focused on by the zipper.

        If there isn't a focused element (because the zipper has zero length),
        this method will raise an IndexError.

        :return: the current item
        """
        return self._items[self.index]
