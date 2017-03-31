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
