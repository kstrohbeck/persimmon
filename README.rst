persimmon
=========

Samples
-------

.. code:: python

  from persimmon.dsl import string, none_of, eol, eof

  comma = string(',')
  elem = none_of(comma).many
  line = elem.many_sep_by(comma)
  csv = (line + eol).many + eof

  def main():
      content = '\n'.join(
          'a,b,c',
          '',
          ',hello world,'
      )
      values = csv.parse(content)

      # values = [
      #     ['a', 'b', 'c'],
      #     [],
      #     ['', 'hello world', '']
      # ]
