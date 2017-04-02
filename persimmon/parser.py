from persimmon import utils


class Result:
    def __init__(self, consumed, expected):
        self.consumed = consumed
        self.expected = expected


class Success(Result):
    def __init__(self, value, consumed=False, expected=None):
        if expected is None:
            expected = []
        super().__init__(consumed, expected)
        self.value = value


class Failure(Result):
    def __init__(self, unexpected, consumed=False, expected=None):
        if expected is None:
            expected = []
        super().__init__(consumed, expected)
        self.unexpected = unexpected


class Parser:
    def do_parse(self, iterator):
        pass

    def expected(self):
        pass

    def parse(self, iterable):
        iterator = utils.RewindIterator(iter(iterable))
        result = self.do_parse(iterator)
        if isinstance(result, Success):
            return result.value
        print(result)
        print('Parsing failure: unexpected {}'.format(result.unexpected))
        print('Expected: {}'.format(', '.join(result.expected)))

    def __or__(self, other):
        if isinstance(other, ChoiceParser):
            return other.prepend(self)
        return ChoiceParser(self, other)

    def __and__(self, other):
        if isinstance(other, ChainParser):
            return other.prepend(self)
        return ChainParser(self, other)

    @staticmethod
    def success(value):
        return SuccessParser(value)

    @staticmethod
    def any_elem():
        return AnyElemParser()

    @staticmethod
    def sequence(seq):
        return AttemptParser(RawSequenceParser(seq))

    @staticmethod
    def string(seq):
        return AttemptParser(RawStringParser(seq))

    @staticmethod
    def digit():
        return AttemptParser(RawDigitParser())

    def map(self, func):
        return MapParser(self, func)


class SuccessParser(Parser):
    def __init__(self, value):
        self._value = value

    def do_parse(self, iterator):
        return Success(self._value)

    def expected(self):
        return []


class AnyElemParser(Parser):
    def do_parse(self, iterator):
        try:
            value = next(iterator)
            return Success(value, consumed=True, expected=['any element'])
        except StopIteration:
            return Failure('end of input', expected=['any element'])

    def expected(self):
        return ['any element']


class RawSequenceParser(Parser):
    def __init__(self, seq):
        self._seq = seq

    def do_parse(self, iterator):
        accum = []
        for s in iter(self._seq):
            value = next(iterator)
            accum.append(value)
            if s != value:
                return Failure(accum, consumed=True, expected=[str(self._seq)])
        return Success(accum, consumed=True, expected=[str(self._seq)])

    def expected(self):
        return [str(self._seq)]


class RawStringParser(Parser):
    def __init__(self, seq):
        self._seq = seq

    def do_parse(self, iterator):
        accum = ''
        for s in iter(self._seq):
            value = next(iterator)
            accum += value
            if s != value:
                return Failure(accum, consumed=True, expected=[self._seq])
        return Success(accum, consumed=True, expected=[self._seq])

    def expected(self):
        return [self._seq]


class AttemptParser(Parser):
    def __init__(self, parser):
        self._parser = parser

    def do_parse(self, iterator):
        with iterator.rewind_point() as point:
            try:
                result = self._parser.do_parse(iterator)
                if isinstance(result, Failure):
                    iterator.rewind_to(point)
                result.consumed = False
                return result
            except StopIteration:
                iterator.rewind_to(point)
                return Failure('end of input', expected=self._parser.expected())

    def expected(self):
        return self._parser.expected()


class RawDigitParser(Parser):
    def do_parse(self, iterator):
        value = next(iterator)
        if str.isdigit(value):
            return Success(int(value), consumed=True, expected=['digit'])
        return Failure(value, consumed=True, expected=['digit'])

    def expected(self):
        return ['digit']


class EndOfFileParser(Parser):
    def do_parse(self, iterator):
        with iterator.rewind_point() as point:
            try:
                value = next(iterator)
                iterator.rewind_to(point)
                return Failure(value, expected=['end of file'])
            except StopIteration:
                return Success(None)

    def expected(self):
        return ['end of file']


class ChoiceParser(Parser):
    def __init__(self, *parsers):
        self._parsers = parsers

    def do_parse(self, iterator):
        first_success = None
        last_failure = None
        expected = []
        for parser in self._parsers:
            result = parser.do_parse(iterator)
            if result.consumed:
                return result
            if isinstance(result, Success):
                if first_success is None:
                    first_success = result
            else:
                last_failure = result
            expected.append(result.expected)
        if first_success is not None:
            first_success.expected = expected
            return first_success
        last_failure.expected = expected
        return last_failure

    def expected(self):
        return [p.expected() for p in self._parsers]

    def __or__(self, other):
        if isinstance(other, ChoiceParser):
            return self.post_extend(other)
        return self.append(other)

    def prepend(self, parser):
        return ChoiceParser(parser, *self._parsers)

    def pre_extend(self, parsers):
        return ChoiceParser(*parsers, *self._parsers)

    def append(self, parser):
        return ChoiceParser(*self._parsers, parser)

    def post_extend(self, parsers):
        return ChoiceParser(*self._parsers, *parsers)


class ChainParser(Parser):
    def __init__(self, *parsers):
        self._parsers = parsers

    def do_parse(self, iterator):
        results = []
        consumed = False
        for parser in self._parsers:
            result = parser.do_parse(iterator)
            consumed = consumed or result.consumed
            if isinstance(result, Failure):
                result.consumed = consumed
                return result
            results.append(result.value)
        return Success(results, consumed=consumed)

    def expected(self):
        pass

    def __and__(self, other):
        if isinstance(other, ChainParser):
            return self.post_extend(other)
        return self.append(other)

    def prepend(self, parser):
        return ChainParser(parser, *self._parsers)

    def pre_extend(self, parsers):
        return ChainParser(*parsers, *self._parsers)

    def append(self, parser):
        return ChainParser(*self._parsers, parser)

    def post_extend(self, parsers):
        return ChainParser(*self._parsers, *parsers)


class MapParser(Parser):
    def __init__(self, parser, func, spread_args=False):
        self._parser = parser
        self._func = func
        self._spread_args = spread_args

    def do_parse(self, iterator):
        result = self._parser.do_parse(iterator)
        if isinstance(result, Success):
            if self._spread_args:
                result.value = self._func(*result.value)
            else:
                result.value = self._func(result.value)
        return result

    def expected(self):
        return self._parser.expected()
