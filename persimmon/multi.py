from persimmon import result
from persimmon.parser import Parser


class MultiChildParser(Parser):
    def __init__(self, parser_factory, parsers):
        super().__init__(parser_factory, all(p.noise for p in parsers))
        self._parsers = parsers

    def do_parse(self, iterator):
        raise NotImplementedError

    @property
    def expected(self):
        raise NotImplementedError

    def combine(self, other):
        if isinstance(other, self.__class__):
            return self.extend(other._parsers)
        return self.append(other)

    def prepend(self, parser):
        return self.__class__(self._parser_factory, [parser] + self._parsers)

    def append(self, parser):
        return self.__class__(self._parser_factory, self._parsers + [parser])

    def extend(self, parsers):
        return self.__class__(self._parser_factory, self._parsers + parsers)


class ChoiceParser(MultiChildParser):
    def do_parse(self, iterator):
        first_success = None
        last_failure = None
        expected = []
        for parser in self._parsers:
            res = parser.do_parse(iterator)
            if res.consumed:
                return res
            if isinstance(res, result.Success):
                first_success = first_success or res
            else:
                last_failure = res
            expected.extend(res.expected)
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
            res = parser.do_parse(iterator)
            consumed = consumed or res.consumed
            if isinstance(res, result.Failure):
                res.consumed = consumed
                return res
            if not parser.noise:
                results.extend(res.values)
        return result.Success(results, consumed=consumed)

    @property
    def expected(self):
        return []

    def __and__(self, other):
        return self.combine(other)
