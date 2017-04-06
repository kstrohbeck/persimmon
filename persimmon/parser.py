from persimmon import result


class Parser:
    def __init__(self, parser_factory, noise):
        self._parser_factory = parser_factory
        self.noise = noise

    def do_parse(self, iterator):
        raise NotImplementedError

    @property
    def expected(self):
        raise NotImplementedError

    def _parse_success(self, values, consumed=False, expected=None):
        return result.Success(values, consumed, expected or self.expected)

    def _parse_failure(self, unexpected, position, consumed=False,
                       expected=None):
        return result.Failure(unexpected, position, consumed,
                              expected or self.expected)

    def parse(self, data):
        iterator = self._parser_factory.make_rewind_iterator(data)
        res = self.do_parse(iterator)
        if res.is_success:
            if len(res.values) == 1:
                return res.values[0]
            return res.values
        print('Parsing failure: unexpected "{}" at {}'.format(res.unexpected,
                                                            res.position))
        print('Expected: {}'.format(', '.join(res.expected)))

    def __or__(self, other):
        return self._parser_factory.combine_choice(self, other)

    def __and__(self, other):
        return self._parser_factory.combine_chain(self, other)

    @property
    def attempt(self):
        return self._parser_factory.make_attempt_parser(self)

    def map(self, func):
        return self._parser_factory.make_map_parser(self, func)

    def always(self, value):
        return self.map(lambda _: value)

    def filter(self, pred):
        return self._parser_factory.make_filter_parser(self, pred)

    def transform(self, transform):
        return self._parser_factory.make_transform_parser(self, transform)

    @property
    def zero_or_more(self):
        return self._parser_factory.make_repeat_parser(self)

    @property
    def one_or_more(self):
        return self._parser_factory.make_repeat_parser(self, min_results=1)

    def zero_or_more_sep_by(self, sep):
        return self.one_or_more_sep_by(sep).default([])

    def one_or_more_sep_by(self, sep):
        return (self & (sep & self).zero_or_more).map(lambda h, t: [h] + t)

    def at_least(self, min_results):
        return self.repeat_between(min_results=min_results)

    def at_most(self, max_results):
        return self.repeat_between(max_results=max_results)

    def repeat_between(self, min_results=0, max_results=None):
        return self._parser_factory.make_repeat_parser(
            self,
            min_results=min_results,
            max_results=max_results
        )

    def repeat(self, num_results):
        return self.repeat_between(num_results, num_results)

    def labeled(self, label):
        return self._parser_factory.make_labeled_parser(self, label)

    @property
    def noisy(self):
        return self._parser_factory.make_noisy_parser(self, noise=True)

    @property
    def not_noisy(self):
        return self._parser_factory.make_noisy_parser(self, noise=False)

    @property
    def exists(self):
        return self.always(True).default(False)
