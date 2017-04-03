import abc


class ParserFactory:
    @abc.abstractmethod
    def make_success_parser(self, value):
        pass

    @abc.abstractmethod
    def make_satisfy_parser(self):
        pass

    def make_any_elem_parser(self):
        return self.make_satisfy_parser().labeled('any element')

    def make_elem_parser(self, el):
        return (
            self.make_satisfy_parser
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
            self.make_satisfy_parser
                .filter(str.isdigit)
                .map(int)
                .labeled('digit')
        )

    @abc.abstractmethod
    def make_choice_parser(self, *parsers):
        pass

    @abc.abstractmethod
    def make_chain_parser(self, *parsers):
        pass

    @abc.abstractmethod
    def make_sequence_parser(self, seq):
        pass

    def make_string_parser(self, string):
        return self.make_sequence_parser(string).map(''.join)

    def make_default_parser(self, parser, value):
        return parser | self.make_success_parser(value)

    @abc.abstractmethod
    def make_eof_parser(self):
        pass

    @abc.abstractmethod
    def make_attempt_parser(self, parser):
        pass

    @abc.abstractmethod
    def make_map_parser(self, parser, func):
        pass

    @abc.abstractmethod
    def combine_choice(self, left, right):
        pass

    @abc.abstractmethod
    def combine_chain(self, left, right):
        pass
