from jft.text_colours.info import f as info
from jft.string.hbar.make import f as hbar

f = lambda py_name, new_fn_text: '\n'.join([
  info(f'{py_name} new_function_text:'),
  new_fn_text,
  hbar(),
])

t = lambda: (
  '\x1b[1;36ma.py new_function_text:\x1b[0;0m\na\nb\nc\nd\n'+'-'*80
  ==
  f('a.py', 'a\nb\nc\nd')
)
