from jft.pickle.load_if_exists import f as load_if_exists
from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdir_if_exists
from pickle import dump

f = lambda filename='durations.pickle': load_if_exists(filename) or {}

temp_dir_path = './_load_durations_if_exists'
temp_file_path = f'{temp_dir_path}/durations.pickle'
data = {'a': 0, 'b': 1, 'c': 2}

def setup_where_pickle_does_not_exist():
  rmdir_if_exists(temp_dir_path)
  mkdirine(temp_dir_path)

def setup_where_pickle_exists():
  setup_where_pickle_does_not_exist()
  with open(temp_file_path, 'wb') as _file:
    dump(data, _file)

def tear_down():
  rmdir_if_exists(temp_dir_path)

def test_where_pickle_does_not_exist():
  setup_where_pickle_does_not_exist()
  observation = f(temp_file_path)
  expectation = {}
  test_result = expectation == observation
  if not test_result:
    print('\n'.join([
      'Case where pickle does not exist failed.',
      f'expectation: {expectation}',
      f'observation: {observation}',
    ]))
  tear_down()
  return test_result

def test_where_pickle_exists():
  setup_where_pickle_exists()
  expectation = data
  observation = f(temp_file_path)
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
