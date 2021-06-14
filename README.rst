persimmon
=========

A Python parser combinator library.

Samples
-------

.. code:: python

  from persimmon import string, none_of

  comma = string(",")
  elem = none_of(comma).many
  line = elem.many_sep_by(comma)
  eol = string("\n")
  csv = (line + eol).many + eof

  def main():
      content = """\
  a,b,c
  
  ,hello world,
  """
  
      values = csv.parse(content)

      # values = [
      #     ['a', 'b', 'c'],
      #     [],
      #     ['', 'hello world', '']
      # ]
