from jft.directory.list_filepaths import f as list_filepaths
from jft.directory.remove import f as remove_dir
from jft.file.pyfile.is_a import f as is_pyfile
from jft.file.save import f as save
from jft.nop_x import f as nopx
from os import mkdir
from os import remove
from os.path import exists

f = lambda root, filepaths=[]: list_filepaths(root, filepaths, is_pyfile)

temp_dir_0 = './_list_pyfilepaths'
temp_dir_1 = f'{temp_dir_0}/_'
temp_files_and_content = [
  (f'{temp_dir_0}/foo.py', 'foo'), (f'{temp_dir_0}/xyz.txt', 'xyz'),
  (f'{temp_dir_1}/abc.txt', 'abc'), (f'{temp_dir_1}/bar.py', 'bar'),
]

def setup():
  [(nopx if exists(δ) else mkdir)(δ) for δ in [temp_dir_0, temp_dir_1]]
  [save(filename, content) for (filename, content) in temp_files_and_content]

def tear_down():
  [remove(filename) for (filename, _) in temp_files_and_content]
  [remove_dir(d) for d in [temp_dir_1, temp_dir_0]]

def t():
  setup()
  test_result = set([
    f'{temp_dir_1}/bar.py',
    f'{temp_dir_0}/foo.py'
  ]) == set(f(temp_dir_0, []))
  tear_down()
  return test_result
