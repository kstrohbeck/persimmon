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
    def __init__(self, noise=False):
        self.noise = noise

    def do_parse(self, iterator):
        pass

    def expected(self):
        pass

    def _parse_success(self, value, consumed=False, expected=None):
        if expected is None:
            expected = self.expected()
        return Success(value, consumed, expected)

    def _parse_failure(self, unexpected, consumed=False, expected=None):
        if expected is None:
            expected = self.expected()
        return Failure(unexpected, consumed, expected)

    def parse(self, data):
        iterator = utils.RewindIterator.make_rewind_iterator(data)
        result = self.do_parse(iterator)
        if isinstance(result, Success):
            return result.value
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
    def satisfy(pred):
        return AttemptParser(RawSatisfyParser(pred))

    @staticmethod
    def elem(el):
        return AttemptParser(RawElemParser(el))

    @staticmethod
    def sequence(seq):
        return AttemptParser(RawSequenceParser(seq))

    @staticmethod
    def string(seq):
        return AttemptParser(RawSequenceParser(seq).map(''.join))

    @staticmethod
    def digit():
        return AttemptParser(RawDigitParser())

    @staticmethod
    def eof():
        return EndOfFileParser()

    def map(self, func):
        return MapParser(self, func)

    def filter(self, pred):
        return FilterParser(self, pred)

    @property
    def zero_or_more(self):
        return RepeatParser(self)

    @property
    def one_or_more(self):
        return RepeatParser(self, min_results=1)

    def at_least(self, min_results):
        return RepeatParser(self, min_results=min_results)

    def at_most(self, max_results):
        return RepeatParser(self, max_results=max_results)

    def repeat_between(self, min_results, max_results):
        return RepeatParser(
            self,
            min_results=min_results,
            max_results=max_results
        )

    def repeat(self, num_results):
        return self.repeat_between(num_results, num_results)

    def labeled(self, label):
        return LabeledParser(self, label)

    @property
    def noisy(self):
        return NoisyParser(self, noise=True)

    @property
    def not_noisy(self):
        return NoisyParser(self, noise=False)


class SuccessParser(Parser):
    def __init__(self, value):
        super().__init__()
        self._value = value

    def do_parse(self, iterator):
        return Success(self._value)

    def expected(self):
        return []


class AnyElemParser(Parser):
    def do_parse(self, iterator):
        try:
            value = next(iterator)
            return self._parse_success(value, consumed=True)
        except StopIteration:
            return self._parse_failure('end of input')

    def expected(self):
        return ['any element']


class RawSatisfyParser(Parser):
    def __init__(self, pred):
        super().__init__(noise=False)
        self._pred = pred

    def do_parse(self, iterator):
        value = next(iterator)
        if not self._pred(value):
            return self._parse_failure(value, consumed=True)
        return self._parse_success(value, consumed=True)

    def expected(self):
        return []


class RawElemParser(Parser):
    def __init__(self, elem):
        super().__init__(noise=True)
        self._elem = elem

    def do_parse(self, iterator):
        value = next(iterator)
        if value != self._elem:
            return self._parse_failure(value, consumed=True)
        return self._parse_success(value, consumed=True)

    def expected(self):
        return [self._elem]


class RawSequenceParser(Parser):
    def __init__(self, seq):
        super().__init__(noise=True)
        self._seq = seq

    def do_parse(self, iterator):
        accum = []
        for s in iter(self._seq):
            value = next(iterator)
            accum.append(value)
            if s != value:
                return self._parse_failure(accum, consumed=True)
        return self._parse_success(accum, consumed=True)

    def expected(self):
        return [str(self._seq)]


class RawDigitParser(Parser):
    def do_parse(self, iterator):
        value = next(iterator)
        if str.isdigit(value):
            return self._parse_success(int(value), consumed=True)
        return self._parse_failure(value, consumed=True)

    def expected(self):
        return ['digit']


class EndOfFileParser(Parser):
    def __init__(self):
        super().__init__(noise=True)

    def do_parse(self, iterator):
        with iterator.rewind_point() as point:
            try:
                value = next(iterator)
                iterator.rewind_to(point)
                return self._parse_failure(value)
            except StopIteration:
                return self._parse_success(None)

    def expected(self):
        return ['end of file']


class SingleChildParser(Parser):
    def __init__(self, child, noise=False):
        noise = noise or child.noise
        super().__init__(noise=noise)
        self._child = child

    def do_parse(self, iterator):
        return self._child.do_parse(iterator)

    def expected(self):
        return self._child.expected()


class AttemptParser(SingleChildParser):
    def do_parse(self, iterator):
        with iterator.rewind_point() as point:
            try:
                result = super().do_parse(iterator)
                if isinstance(result, Failure):
                    iterator.rewind_to(point)
                result.consumed = False
                return result
            except StopIteration:
                iterator.rewind_to(point)
                return self._parse_failure('end of input')


class MapParser(SingleChildParser):
    def __init__(self, child, func, spread_args=False):
        super().__init__(child)
        self._func = func
        self._spread_args = spread_args

    def do_parse(self, iterator):
        result = super().do_parse(iterator)
        if isinstance(result, Success):
            if self._spread_args:
                result.value = self._func(*result.value)
            else:
                result.value = self._func(result.value)
        return result


class FilterParser(SingleChildParser):
    def __init__(self, child, pred, spread_args=False):
        super().__init__(child)
        self._pred = pred
        self._spread_args = spread_args

    def do_parse(self, iterator):
        result = super().do_parse(iterator)
        if isinstance(result, Success) and not self._pred(result.value):
            return self._parse_failure('bad input', consumed=True)
        return result

    def expected(self):
        return []


class RepeatParser(SingleChildParser):
    def __init__(self, child, min_results=0, max_results=None):
        super().__init__(child)
        self._min_results = min_results
        self._max_results = max_results

    def do_parse(self, iterator):
        results = []
        consumed = False
        expected = []
        while self._max_results is None or len(results) < self._max_results:
            result = super().do_parse(iterator)
            consumed = consumed or result.consumed
            expected = result.expected
            if isinstance(result, Success):
                results.append(result.value)
            else:
                if len(results) < self._min_results:
                    return Failure(
                        result.unexpected,
                        consumed=consumed,
                        expected=expected
                    )
                break
        return Success(results, consumed=consumed, expected=expected)


class LabeledParser(SingleChildParser):
    def __init__(self, child, label):
        super().__init__(child)
        self._label = label

    def do_parse(self, iterator):
        result = super().do_parse(iterator)
        if not result.consumed:
            result.expected = self.expected()
        return result

    def expected(self):
        return [self._label]


class NoisyParser(SingleChildParser):
    def __init__(self, child, noise):
        super().__init__(child, noise=noise)


class MultiChildParser(Parser):
    def __init__(self, *parsers):
        super().__init__(noise=all(p.noise for p in parsers))
        self._parsers = parsers

    def combine(self, other):
        if isinstance(other, self.__class__):
            return self.extend(other)
        return self.append(other)

    def prepend(self, parser):
        return self.__class__(parser, *self._parsers)

    def append(self, parser):
        return self.__class__(*self._parsers, parser)

    def extend(self, parsers):
        return self.__class__(*self._parsers, *parsers)


class ChoiceParser(MultiChildParser):
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
            expected.extend(result.expected)
        if first_success is not None:
            first_success.expected = expected
            return first_success
        last_failure.expected = expected
        return last_failure

    def expected(self):
        return [p.expected() for p in self._parsers]

    def __or__(self, other):
        return self.combine(other)


class ChainParser(MultiChildParser):
    def do_parse(self, iterator):
        results = []
        consumed = False
        for parser in self._parsers:
            result = parser.do_parse(iterator)
            consumed = consumed or result.consumed
            if isinstance(result, Failure):
                result.consumed = consumed
                return result
            if not parser.noise:
                results.append(result.value)
        if len(results) == 1:
            return Success(results[0], consumed=consumed)
        return Success(results, consumed=consumed)

    def expected(self):
        pass

    def __and__(self, other):
        return self.combine(other)

    def map(self, func):
        return MapParser(self, func, spread_args=True)
