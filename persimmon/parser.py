from persimmon import utils


class Parser:
    def do_parse(self, iterator):
        pass

    def parse(self, iterable):
        iterator = utils.RewindIterator(iter(iterable))
        return self.do_parse(iterator)
