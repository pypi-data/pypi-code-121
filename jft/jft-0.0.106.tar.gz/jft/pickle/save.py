from pickle import dump
from os.path import exists
from jft.pickle.load_if_exists import f as load_if_exists
from jft.directory.remove import f as rmdir_if_exists
from jft.file.remove import f as remove
from os import mkdir

def f(data, path):
  if '/' in path:
    dir_name = '/'.join(path.split('/')[:-1])
    existed = exists(dir_name)
    
    if not existed:
      mkdir(dir_name)
  
  with open(path, 'wb') as _file:
    dump(data, _file)

temp_dir_path = './_save'
temp_file_path = f'{temp_dir_path}/x.pickle'
data = {'a': 0, 'b': 1, 'c': {'x': True, 'y': False}}

def setup(): rmdir_if_exists(temp_dir_path)

def tear_down():
  remove(temp_file_path)
  rmdir_if_exists(temp_dir_path)

def t():
  setup()
  expectation = data
  f(data, temp_file_path)
  observation = load_if_exists(temp_file_path)
  test_result = expectation == observation
  if not test_result:
    print('\n'.join([
      'Case where pickle does not exist failed.',
      f'expectation: {expectation}',
      f'observation: {observation}',
    ]))
  tear_down()
  return test_result
