from jft.file.load import f as load
from jft.file.save import f as save
from jft.directory.make import f as mkdir
from jft.file.remove import f as remove
from jft.directory.remove import f as remove_dir

f = lambda x: {φ: load(φ) for φ in x}

_root = '../temp_pyfiles_to_dict'
_Π = [(f'{_root}/foo.py', 'foo'), (f'{_root}/bar.py', 'bar')]

tear_down = lambda: [*[remove(π_f) for (π_f, _) in _Π], remove_dir(_root)]
setup = lambda: [mkdir(_root), *[save(π_f, π_d) for π_f, π_d in _Π]]

def t():
  setup()
  expectation = {f'{_root}/foo.py': 'foo', f'{_root}/bar.py': 'bar'}
  observation = f([f'{_root}/foo.py', f'{_root}/bar.py'])
  test_result = expectation == observation
  tear_down()
  return test_result
