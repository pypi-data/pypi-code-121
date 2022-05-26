from jft.directory.make import f as mkdir
from jft.file.save import f as save
from jft.directory.list_pyfilepaths import f as list_py_files
from jft.strings.pyfiles.filter_out_items import f as ignore_protected
from jft.file.pyfile.dismantle import f as dismantle
from jft.file.load import f as load
from jft.directory.remove import f as rmdir
from jft.directory.exists import f as exists

ignorable = [f'./jft/{_}.py' for _ in [
  'jft',
  'file/load',
  'terminal',
  'refactor_recommender'
]]

f = lambda root='.': [
  dismantle(π_filename=π, root=root)
  for π in ignore_protected(list_py_files(root, []), ignorable)
]

_root = '../temp_pyfiles_dismantle'
K = ['foo', 'bar']
_Π_path_original = {k: f'{_root}/{k}.py' for k in K}
_Π_path_new = {k: f'{_root}/_{k}.py' for k in K}
_Π_content = {k: '\n'.join([
    '# Header comment',
    '',
    f'def {k}(x, y, z):',
    '  return x + y + z',
    '',
    "if __name__ == '__main__':",
    f'  print({k}(2, 3, 4))',
    ''
  ])
  for k in K
}

def setup(): return [
  mkdir(_root),
  *[save(_Π_path_original[k], _Π_content[k]) for k in K]
]

tear_down = lambda: rmdir(_root)

def t():
  setup()

  _Π_original_content = {k: load(_Π_path_original[k]) for k in K}
  z = f(_root)
  _Π_observed_updated = {k: load(_Π_path_original[k]) for k in K}
  _Π_observed_new = {k: load(_Π_path_new[k]) for k in K}
  
  tear_down()

  return all([
    _Π_original_content != _Π_observed_updated,
    *[len(_Π_original_content[k]) > len(_Π_observed_updated[k]) for k in K],
    *[len(_Π_original_content[k]) > len(_Π_observed_new[k]) for k in K],
    *[k in _Π_observed_updated[k] for k in K],
    *[f'_{k}' in _Π_observed_updated[k] for k in K],
    *[k in _Π_observed_updated[k] for k in K],
    not exists(_root)
  ])
