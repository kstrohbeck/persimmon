from persimmon.standard import StandardParserFactory

_factory = StandardParserFactory()

success = _factory.make_success_parser
satisfy = _factory.make_satisfy_parser()
any_elem = _factory.make_any_elem_parser()
elem = _factory.make_elem_parser
one_of = _factory.make_one_of_parser
none_of = _factory.make_none_of_parser
digit = _factory.make_digit_parser()
choice = _factory.make_choice_parser
chain = _factory.make_chain_parser
sequence = _factory.make_sequence_parser
string = _factory.make_string_parser
eof = _factory.make_eof_parser()
delayed = _factory.make_delayed_parser
