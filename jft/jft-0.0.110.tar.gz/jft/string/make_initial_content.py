from jft.text_colours.info import f as info
from jft.string.hbar.make import f as hbar

f = lambda π_filename, initial_content: '\n'.join([
  info(f'{π_filename} initial_content:'),
  initial_content,
  hbar()
])

k = 'abc\ndef\nghi\njkl'
n = 'abc.py'

t = lambda: f'\x1b[1;36m{n} initial_content:\x1b[0;0m\n{k}\n'+'-'*80 == f(n, k)
