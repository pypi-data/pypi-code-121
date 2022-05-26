from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdirie
from jft.file.save import f as save
from jft.string.has_seven_digits import f as has_7_digits
from jft.string.has_at_symbol import f as has_at_symbol
from jft.string.has_lowercase import f as has_lowercase

filename = 'username.secret'

def f(root='.'):
  _ = f'{root}/{filename}'
  with open(_, 'r') as φ:
    return φ.readlines()[0]

_root = '../temp_secret_username'
_filepath = f'{_root}/{filename}'

setup = lambda: [mkdirine(_root), save(_filepath, 'z3525170@ad.unsw.edu.au')]

tear_down = lambda: rmdirie(_root)

def t():
  setup()
  z = f(_root)
  return all([has_7_digits(z), has_at_symbol(z), has_lowercase(z)])
