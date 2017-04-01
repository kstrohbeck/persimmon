from persimmon import utils


class Success:
    def __init__(self, value):
        self.value = value


class Failure:
    def __init__(self, unexpected):
        self.unexpected = unexpected


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

    @staticmethod
    def any_elem():
        return AnyElemParser()


class SuccessParser(Parser):
    def __init__(self, value):
        self._value = value

    def do_parse(self, iterator):
        return self._value

    def expected(self):
        return []


class AnyElemParser(Parser):
    def do_parse(self, iterator):
        try:
            value = next(iterator)
            return value
        except StopIteration:
            # TODO: return "end of input" error
            pass

    def expected(self):
        return ['any element']


class SequenceParser(Parser):
    def __init__(self, seq):
        self._seq = seq

    def do_parse(self, iterator):
        with iterator.rewind_point() as point:
            accum = []
            try:
                for s in iter(self._seq):
                    value = next(iterator)
                    if s != value:
                        raise StopIteration
                    accum.append(value)
            except StopIteration:
                iterator.rewind(point)
                # TODO: return ??? error
            return accum

    def expected(self):
        return [str(self._seq)]


class AttemptParser(Parser):
    def __init__(self, parser):
        self._parser = parser

    def do_parse(self, iterator):
        with iterator.rewind_point() as point:
            try:
                return self._parser.do_parse(iterator)
            except StopIteration:
                iterator.rewind(point)
                return Failure('end of input')

    def expected(self):
        return self._parser.expected()
