class ParserFactory:
    def make_rewind_iterator(self, data):
        raise NotImplementedError

    def make_success_parser(self, value):
        raise NotImplementedError

    def make_satisfy_parser(self, steps=None):
        raise NotImplementedError

    def make_any_elem_parser(self):
        return self.make_satisfy_parser().labeled('any element')

    def make_elem_parser(self, el):
        return (
            self.make_satisfy_parser()
                .filter(lambda e: e == el)
                .noisy
                .labeled(el)
        )

    def make_one_of_parser(self, els):
        return (
            self.make_satisfy_parser()
            .filter(lambda e: e in els)
            .labeled(els)
        )

    def make_none_of_parser(self, els):
        return self.make_satisfy_parser().filter(lambda e: e not in els)

    def make_digit_parser(self):
        return (
            self.make_satisfy_parser()
                .filter(str.isdigit)
                .map(int)
                .labeled('digit')
        )

    def make_choice_parser(self, parsers):
        raise NotImplementedError

    def make_chain_parser(self, parsers):
        raise NotImplementedError

    def make_sequence_parser(self, seq):
        raise NotImplementedError

    def make_string_parser(self, string):
        return self.make_sequence_parser(string).map(''.join)

    def make_default_parser(self, parser, value):
        return parser | self.make_success_parser(value)

    def make_eof_parser(self):
        raise NotImplementedError

    def make_attempt_parser(self, parser):
        raise NotImplementedError

    def make_map_parser(self, parser, func):
        raise NotImplementedError

    def make_filter_parser(self, parser, pred):
        raise NotImplementedError

    def make_transform_parser(self, parser, transform):
        raise NotImplementedError

    def combine_choice(self, left, right):
        raise NotImplementedError

    def combine_chain(self, left, right):
        raise NotImplementedError

    def make_repeat_parser(self, parser, min_results=0, max_results=None):
        raise NotImplementedError

    def make_labeled_parser(self, parser, label):
        raise NotImplementedError

    def make_noisy_parser(self, parser, noise):
        raise NotImplementedError

    def make_delayed_parser(self, parser_func):
        raise NotImplementedError
