from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdirie
from jft.file.save import f as save
from jft.string.password.has_chars_from_3_sets import f as has_ch_from_3

filename = 'password.secret'

def f(root='.'):
  _ = f'{root}/{filename}'
  with open(_, 'r') as φ:
    return φ.readlines()[0]

_root = '../temp_secret_password'
_filepath = f'{_root}/{filename}'
_content = 'abc123!@#JKLmno'

setup = lambda: [mkdirine(_root), save(_filepath, _content)]
tear_down = lambda: rmdirie(_root)

def t():
  setup()
  z = f(_root)
  result_has_characters_from_3_distinct_sets = has_ch_from_3(z)
  tear_down()
  return all([result_has_characters_from_3_distinct_sets, z == _content])
