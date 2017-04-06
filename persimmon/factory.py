from abc import abstractmethod


class ParserFactory:
    @abstractmethod
    def make_rewind_iterator(self, data):
        pass

    @abstractmethod
    def make_success_parser(self, value):
        pass

    @abstractmethod
    def make_satisfy_parser(self):
        pass

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
        return self.make_satisfy_parser.filter(lambda e: e in els).labeled(els)

    def make_none_of_parser(self, els):
        return self.make_satisfy_parser.filter(lambda e: e not in els)

    def make_digit_parser(self):
        return (
            self.make_satisfy_parser()
                .filter(str.isdigit)
                .map(int)
                .labeled('digit')
        )

    @abstractmethod
    def make_choice_parser(self, parsers):
        pass

    @abstractmethod
    def make_chain_parser(self, parsers):
        pass

    @abstractmethod
    def make_sequence_parser(self, seq):
        pass

    def make_string_parser(self, string):
        return self.make_sequence_parser(string).map(''.join)

    def make_default_parser(self, parser, value):
        return parser | self.make_success_parser(value)

    @abstractmethod
    def make_eof_parser(self):
        pass

    @abstractmethod
    def make_attempt_parser(self, parser):
        pass

    @abstractmethod
    def make_map_parser(self, parser, func):
        pass

    @abstractmethod
    def make_filter_parser(self, parser, pred):
        pass

    @abstractmethod
    def make_transform_parser(self, parser, transform):
        pass

    @abstractmethod
    def combine_choice(self, left, right):
        pass

    @abstractmethod
    def combine_chain(self, left, right):
        pass

    @abstractmethod
    def make_repeat_parser(self, parser, min_results=0, max_results=None):
        pass

    @abstractmethod
    def make_labeled_parser(self, parser, label):
        pass

    @abstractmethod
    def make_noisy_parser(self, parser, noise):
        pass

    @abstractmethod
    def make_delayed_parser(self, parser_func):
        pass
