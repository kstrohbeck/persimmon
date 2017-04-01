from persimmon import utils


class Expected:
    pass


class Parser:
    def do_parse(self, iterator):
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
