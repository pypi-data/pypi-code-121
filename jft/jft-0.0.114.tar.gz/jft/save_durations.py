from jft.pickle.save import f as save
from os.path import exists
from jft.pickle.load_if_exists import f as load_if_exists
from os import remove

f = lambda durations: save(durations, 'durations.pickle')

dir_path = '.'
file_path = f'{dir_path}/durations.pickle'
data = {'a': 0, 'b': 1, 'c': {'x': True, 'y': False}}

def setup():
  if exists(file_path):
    backup = load_if_exists(file_path)
    remove(file_path)
    return backup

def tear_down(backup):
  if backup:
    f(backup)
  else:
    remove(file_path)

def t():
  backup = setup()
  expectation = data
  f(data)
  observation = load_if_exists(file_path)
  test_result = expectation == observation
  if not test_result:
    print('\n'.join([
      'Case where pickle does not exist failed.',
      f'expectation: {expectation}',
      f'observation: {observation}',
    ]))
  tear_down(backup)
  return test_result