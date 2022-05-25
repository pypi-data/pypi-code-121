from os.path import exists
from os import mkdir
from jft.file.save import f as save
from os import remove
from jft.directory.remove import f as remove_dir

def f(filename):
  with open(filename, 'r', encoding='utf8') as φ:
    return φ.read()

temp_dir_0 = './_temp_file_load'
temp_files_and_content = [(f'{temp_dir_0}/foo.py', 'foo')]

def setup():
  [mkdir(temp_dir) for temp_dir in [temp_dir_0] if not exists(temp_dir)]
  [save(filename, content) for (filename, content) in temp_files_and_content]

def tear_down():
  [remove(filename) for (filename, _) in temp_files_and_content]
  remove_dir(temp_dir_0)

def t():
  setup()
  test_result = 'foo' == f(f'{temp_dir_0}/foo.py')
  tear_down()
  return test_result