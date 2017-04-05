from persimmon.parser import Parser


class SuccessParser(Parser):
    def __init__(self, parser_factory, value):
        super().__init__(parser_factory, False)
        self._value = value

    def do_parse(self, iterator):
        return self._parse_success([self._value])

    @property
    def expected(self):
        return []


class SatisfyParser(Parser):
    def __init__(self, parser_factory, steps):
        super().__init__(parser_factory, False)
        self._steps = steps or []

    def do_parse(self, iterator):
        with iterator.rewind_point() as point:
            try:
                initial = next(iterator)
                value = initial
                for step in self._steps:
                    passes, value = step(value)
                    if not passes:
                        iterator.rewind_to(point)
                        return self._parse_failure(initial)
                return self._parse_success([value], consumed=True)
            except StopIteration:
                iterator.rewind_to(point)
                return self._parse_failure('end of input')

    @property
    def expected(self):
        return []

    def map(self, func):
        return self.with_step(self.map_step(func))

    def filter(self, pred):
        return self.with_step(self.filter_step(pred))

    def transform(self, transform):
        return self.with_step(self.transform_step(transform))

    def with_step(self, step):
        return self._parser_factory.make_satisfy_parser(self._steps + [step])

    @staticmethod
    def map_step(func):
        return lambda value: (True, func(value))

    @staticmethod
    def filter_step(pred):
        return lambda value: (pred(value), value)

    @staticmethod
    def transform_step(transform):
        def run(value):
            new_value = transform(value)
            if new_value is None:
                return False, value
            return True, new_value
        return run


class RawSequenceParser(Parser):
    def __init__(self, parser_factory, seq):
        super().__init__(parser_factory, True)
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
    def __init__(self, parser_factory):
        super().__init__(parser_factory, True)

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
