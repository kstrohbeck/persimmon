from persimmon import utils


class Result:
    def __init__(self, consumed, expected):
        self.consumed = consumed
        self.expected = expected


class Success(Result):
    def __init__(self, values, consumed=False, expected=None):
        if expected is None:
            expected = []
        super().__init__(consumed, expected)
        self.values = values


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

    @property
    def expected(self):
        raise NotImplementedError

    def _parse_success(self, values, consumed=False, expected=None):
        if expected is None:
            expected = self.expected
        return Success(values, consumed, expected)

    def _parse_failure(self, unexpected, consumed=False, expected=None):
        if expected is None:
            expected = self.expected
        return Failure(unexpected, consumed, expected)

    def parse(self, data):
        iterator = utils.RewindIterator.make_rewind_iterator(data)
        result = self.do_parse(iterator)
        if isinstance(result, Success):
            if len(result.values) == 1:
                return result.values[0]
            return result.values
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
        return SatisfyParser().labeled('any element')

    @staticmethod
    def satisfy(pred):
        return SatisfyParser().filter(pred)

    @staticmethod
    def elem(el):
        return SatisfyParser().filter(lambda e: e == el).noisy.labeled(el)

    @staticmethod
    def one_of(*els):
        return SatisfyParser().filter(lambda e: e in els).labeled(els)

    @staticmethod
    def none_of(*els):
        return SatisfyParser().filter(lambda e: e not in els)

    @staticmethod
    def sequence(seq):
        return AttemptParser(RawSequenceParser(seq))

    @staticmethod
    def string(seq):
        return AttemptParser(RawSequenceParser(seq).map(''.join))

    @staticmethod
    def digit():
        return SatisfyParser().filter(str.isdigit).map(int).labeled('digit')

    @staticmethod
    def eof():
        return EndOfFileParser()

    @property
    def attempt(self):
        return AttemptParser(self)

    def default(self, value):
        return self | Parser.success(value)

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

    @property
    def exists(self):
        return self.map(lambda _: True) | Parser.success(False)


class SuccessParser(Parser):
    def __init__(self, value):
        super().__init__()
        self._value = value

    def do_parse(self, iterator):
        return Success([self._value])

    @property
    def expected(self):
        return []


class SatisfyStep:
    def map(self, value):
        return value

    def filter(self, _):
        return True


class MapStep(SatisfyStep):
    def __init__(self, func):
        self._func = func

    def map(self, value):
        return self._func(value)


class FilterStep(SatisfyStep):
    def __init__(self, pred):
        self._pred = pred

    def filter(self, value):
        return self._pred(value)


class SatisfyParser(Parser):
    def __init__(self, steps=None):
        super().__init__(noise=False)
        self._steps = [] if steps is None else steps

    def do_parse(self, iterator):
        with iterator.rewind_point() as point:
            try:
                initial = next(iterator)
                value = initial
                for step in self._steps:
                    if not step.filter(value):
                        iterator.rewind_to(point)
                        return self._parse_failure(initial)
                    value = step.map(value)
                return self._parse_success([value], consumed=True)
            except StopIteration:
                iterator.rewind_to(point)
                return self._parse_failure('end of input')

    @property
    def expected(self):
        return []

    def map(self, func):
        return SatisfyParser(self._steps + [MapStep(func)])

    def filter(self, pred):
        return SatisfyParser(self._steps + [FilterStep(pred)])


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
        return self._parse_success([accum], consumed=True)

    @property
    def expected(self):
        return [str(self._seq)]


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
                return self._parse_success([])

    @property
    def expected(self):
        return ['end of file']


class SingleChildParser(Parser):
    def __init__(self, child, noise=False):
        noise = noise or child.noise
        super().__init__(noise=noise)
        self._child = child

    def do_parse(self, iterator):
        return self._child.do_parse(iterator)

    @property
    def expected(self):
        return self._child.expected


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
    def __init__(self, child, func):
        super().__init__(child)
        self._func = func

    def do_parse(self, iterator):
        result = super().do_parse(iterator)
        if isinstance(result, Success):
            if len(result.values) == 1:
                result.values = [self._func(result.values[0])]
            else:
                result.values = [self._func(*result.values)]
        return result


class FilterParser(SingleChildParser):
    def __init__(self, child, pred):
        super().__init__(child)
        self._pred = pred

    def do_parse(self, iterator):
        result = super().do_parse(iterator)
        if isinstance(result, Success):
            if len(result.values) == 1:
                passes = self._pred(result.values[0])
            else:
                passes = self._pred(*result.values)
            if not passes:
                return self._parse_failure('bad input', consumed=True)
        return result

    @property
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
                results.extend(result.values)
            else:
                if len(results) < self._min_results:
                    return Failure(
                        result.unexpected,
                        consumed=consumed,
                        expected=expected
                    )
                break
        return Success([results], consumed=consumed, expected=expected)


class LabeledParser(SingleChildParser):
    def __init__(self, child, label):
        super().__init__(child)
        self._label = label

    def do_parse(self, iterator):
        result = super().do_parse(iterator)
        if not result.consumed:
            result.expected = self.expected
        return result

    @property
    def expected(self):
        return [self._label]


class NoisyParser(SingleChildParser):
    def __init__(self, child, noise):
        super().__init__(child, noise=noise)


class MultiChildParser(Parser):
    def __init__(self, *parsers):
        super().__init__(noise=all(p.noise for p in parsers))
        self._parsers = parsers

    @property
    def expected(self):
        raise NotImplementedError

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

    @property
    def expected(self):
        return [p.expected for p in self._parsers]

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
                results.extend(result.values)
        return Success(results, consumed=consumed)

    @property
    def expected(self):
        return []

    def __and__(self, other):
        return self.combine(other)
