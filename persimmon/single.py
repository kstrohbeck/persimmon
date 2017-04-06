from persimmon.parser import Parser


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
            except StopIteration:
                iterator.rewind_to(point)
                return self._parse_failure('end of input', iterator.position)
            if not res.is_success:
                iterator.rewind_to(point)
            res.consumed = False
            return res


def _apply_to_varying(func, values):
    return func(values[0]) if len(values) == 1 else func(*values)


class MapParser(SingleChildParser):
    def __init__(self, parser_factory, child, func):
        super().__init__(parser_factory, False, child)
        self._func = func

    def do_parse(self, iterator):
        res = super().do_parse(iterator)
        if res.is_success:
            res.values = [_apply_to_varying(self._func, res.values)]
        return res


class FilterParser(SingleChildParser):
    def __init__(self, parser_factory, child, pred):
        super().__init__(parser_factory, None, child)
        self._pred = pred

    def do_parse(self, iterator):
        res = super().do_parse(iterator)
        if res.is_success:
            passes = _apply_to_varying(self._pred, res.values)
            if not passes:
                return self._parse_failure('bad input', iterator.position,
                                           consumed=True)
        return res

    @property
    def expected(self):
        return []


class TransformParser(SingleChildParser):
    def __init__(self, parser_factory, child, transform):
        super().__init__(parser_factory, None, child)
        self._transform = transform

    def do_parse(self, iterator):
        res = super().do_parse(iterator)
        if res.is_success:
            new_value = _apply_to_varying(self._transform, res.values)
            if new_value is None:
                return self._parse_failure('bad input', iterator.position,
                                           consumed=True)
            res.values = [new_value]
        return res


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
            if res.is_success:
                results.extend(res.values)
            else:
                if len(results) < self._min_results:
                    return self._parse_failure(
                        res.unexpected,
                        iterator.position,
                        consumed,
                        expected
                    )
                break
        return self._parse_success([results], consumed, expected)


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

    def _inject(self, parser):
        return self._parser_factory.make_labeled_parser(parser, self._label)

    def map(self, func):
        return self._inject(self._child.map(func))

    def filter(self, pred):
        return self._inject(self._child.filter(pred))

    def transform(self, transform):
        return self._inject(self._child.transform(transform))


class NoisyParser(SingleChildParser):
    def _inject(self, parser):
        return self._parser_factory.make_noisy_parser(parser, self.noise)

    def map(self, func):
        return self._inject(self._child.map(func))

    def filter(self, pred):
        return self._inject(self._child.filter(pred))

    def transform(self, transform):
        return self._inject(self._child.transform(transform))


class DelayedParser(SingleChildParser):
    def do_parse(self, iterator):
        if hasattr(self._child, '__call__'):
            self._child = self._child(self)
        return super().do_parse(iterator)

    @property
    def expected(self):
        # TODO: is it safe to eval _delayed to get this?
        return []
