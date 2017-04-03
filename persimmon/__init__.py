from persimmon.parser import BaseParser


success = BaseParser.success
any_elem = BaseParser.any_elem()
satisfy = BaseParser.satisfy
elem = BaseParser.elem
sequence = BaseParser.sequence
string = BaseParser.string
digit = BaseParser.digit()
eof = BaseParser.eof()
one_of = BaseParser.one_of
none_of = BaseParser.none_of
choice = BaseParser.choice
delayed = BaseParser.delayed
