from jft.text_colours.info import f as info
from jft.string.hbar.make import f as hbar

f = lambda x: '\n'.join([f'{info("python_file:")} {x}', hbar('=')])

t = lambda: all([
  '\x1b[1;36mpython_file:\x1b[0;0m abc.py\n'+'='*80 == f('abc.py'),
  '\x1b[1;36mpython_file:\x1b[0;0m xyz.py\n'+'='*80 == f('xyz.py')
])
