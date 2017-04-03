from persimmon.parser import result, Parser


class SingleChildParser(Parser):
    def __init__(self, parser_factory, noise, child):
        noise = child.noise if noise is None else noise
        super().__init__(parser_factory, noise)
        self._child = child

    def do_parse(self, iterator):
        return self._child.do_parse(iterator)

    @property
    def expected(self):
        return self._child.expected


class AttemptParser(SingleChildParser):
    def __init__(self, parser_factory, child):
        super().__init__(parser_factory, None, child)

    def do_parse(self, iterator):
        with iterator.rewind_point() as point:
            try:
                res = super().do_parse(iterator)
                if isinstance(res, result.Failure):
                    iterator.rewind_to(point)
                res.consumed = False
                return res
            except StopIteration:
                iterator.rewind_to(point)
                return self._parse_failure('end of input')


class MapParser(SingleChildParser):
    def __init__(self, parser_factory, child, func):
        super().__init__(parser_factory, False, child)
        self._func = func

    def do_parse(self, iterator):
        res = super().do_parse(iterator)
        if isinstance(res, result.Success):
            if len(res.values) == 1:
                res.values = [self._func(res.values[0])]
            else:
                res.values = [self._func(*res.values)]
        return res


class FilterParser(SingleChildParser):
    def __init__(self, parser_factory, child, pred):
        super().__init__(parser_factory, None, child)
        self._pred = pred

    def do_parse(self, iterator):
        res = super().do_parse(iterator)
        if isinstance(res, result.Success):
            if len(res.values) == 1:
                passes = self._pred(res.values[0])
            else:
                passes = self._pred(*res.values)
            if not passes:
                return self._parse_failure('bad input', consumed=True)
        return res

    @property
    def expected(self):
        return []


class RepeatParser(SingleChildParser):
    def __init__(self, parser_factory, child, min_results=0, max_results=None):
        super().__init__(parser_factory, None, child)
        self._min_results = min_results
        self._max_results = max_results

    def do_parse(self, iterator):
        results = []
        consumed = False
        expected = []
        while self._max_results is None or len(results) < self._max_results:
            res = super().do_parse(iterator)
            consumed = consumed or res.consumed
            expected = res.expected
            if isinstance(res, result.Success):
                results.extend(res.values)
            else:
                if len(results) < self._min_results:
                    return result.Failure(
                        res.unexpected,
                        consumed=consumed,
                        expected=expected
                    )
                break
        return result.Success([results], consumed=consumed, expected=expected)


class LabeledParser(SingleChildParser):
    def __init__(self, parser_factory, child, label):
        super().__init__(parser_factory, None, child)
        self._label = label

    def do_parse(self, iterator):
        res = super().do_parse(iterator)
        if not res.consumed:
            res.expected = self.expected
        return res

    @property
    def expected(self):
        return [self._label]

    def map(self, func):
        return self._parser_factory.make_labeled_parser(
            self._child.map(func),
            self._label
        )

    def filter(self, pred):
        return self._parser_factory.make_labeled_parser(
            self._child.filter(pred),
            self._label
        )

    def transform(self, transform):
        return self._parser_factory.make_labeled_parser(
            self._child.transform(transform),
            self._label
        )


class NoisyParser(SingleChildParser):
    def map(self, func):
        return self._parser_factory.make_noisy_parser(
            self._child.map(func),
            self.noise
        )

    def filter(self, pred):
        return self._parser_factory.make_noisy_parser(
            self._child.filter(pred),
            self.noise
        )

    def transform(self, transform):
        return self._parser_factory.make_noisy_parser(
            self._child.transform(transform),
            self.noise
        )
