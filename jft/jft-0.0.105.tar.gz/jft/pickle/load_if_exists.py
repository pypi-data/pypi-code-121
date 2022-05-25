from os.path import exists
from pickle import load
from pickle import dump
from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdir_if_exists

def f(pickle_filename):
  if exists(pickle_filename):
    with open(pickle_filename, 'rb') as _file:
      return load(_file)

temp_dir_path = './temp_pickle_load_if_exists'
temp_file_path = f'{temp_dir_path}/x.pickle'
data = {'a': 0, 'b': 1, 'c': {'x': True, 'y': False}}

def setup_where_pickle_does_not_exist():
  rmdir_if_exists(temp_dir_path)
  mkdirine(temp_dir_path)

def tear_down():
  rmdir_if_exists(temp_dir_path)

def test_where_pickle_does_not_exist():
  setup_where_pickle_does_not_exist()
  observation = f(temp_file_path)
  expectation = None
  test_result = expectation == observation
  if not test_result:
    print('\n'.join([
      'Case where pickle does not exist failed.',
      f'expectation: {expectation}',
      f'observation: {observation}',
    ]))
  tear_down()
  return test_result

def setup_where_pickle_exists():
  rmdir_if_exists(temp_dir_path)
  mkdirine(temp_dir_path)
  with open(temp_file_path, 'wb') as _file:
    dump(data, _file)

def test_where_pickle_exists():
  setup_where_pickle_exists()
  observation = f(temp_file_path)
  expectation = data
  test_result = expectation == observation
  if not test_result:
    print('\n'.join([
      'Case where pickle exists failed.',
      f'expectation: {expectation}',
      f'observation: {observation}',
    ]))
  tear_down()
  return test_result

t = lambda: all([
  test_where_pickle_does_not_exist(),
  test_where_pickle_exists()
])
