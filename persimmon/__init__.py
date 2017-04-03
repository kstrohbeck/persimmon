from persimmon import primitive, single, multi, utils
from persimmon.factory import ParserFactory


class StandardParserFactory(ParserFactory):
    def make_rewind_iterator(self, data):
        return utils.RewindIterator.make_rewind_iterator(data)

    def make_success_parser(self, value):
        return primitive.SuccessParser(self, value)

    def make_satisfy_parser(self):
        return primitive.SatisfyParser(self, [])

    def make_choice_parser(self, parsers):
        return multi.ChoiceParser(self, parsers)

    def make_chain_parser(self, parsers):
        return multi.ChainParser(self, parsers)

    def make_sequence_parser(self, seq):
        return single.AttemptParser(
            self,
            primitive.RawSequenceParser(self, seq)
        )

    def make_eof_parser(self):
        return primitive.EndOfFileParser(self)

    def make_attempt_parser(self, parser):
        return single.AttemptParser(self, parser)

    def make_map_parser(self, parser, func):
        return single.MapParser(self, parser, func)

    def make_filter_parser(self, parser, pred):
        return single.FilterParser(self, parser, pred)

    def combine_choice(self, left, right):
        # TODO: how to combine?
        pass

    def combine_chain(self, left, right):
        # TODO: how to combine?
        pass

    def make_repeat_parser(self, parser, min_results=0, max_results=None):
        return single.RepeatParser(self, parser, min_results, max_results)

    def make_labeled_parser(self, parser, label):
        return single.LabeledParser(self, parser, label)

    def make_noisy_parser(self, parser, noise):
        return single.NoisyParser(self, noise, parser)

    def make_delayed_parser(self, parser_func):
        return single.DelayedParser(self, False, parser_func)
