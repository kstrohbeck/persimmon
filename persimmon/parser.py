from persimmon import utils


class Parser:
    def do_parse(self, iterator):
        pass

    def expected(self):
        pass

    def parse(self, iterable):
        iterator = utils.RewindIterator(iter(iterable))
        return self.do_parse(iterator)

    @staticmethod
    def success(value):
        return SuccessParser(value)


class SuccessParser(Parser):
    def __init__(self, value):
        self._value = value

    def do_parse(self, iterator):
        return self._value

    def expected(self):
        return []
