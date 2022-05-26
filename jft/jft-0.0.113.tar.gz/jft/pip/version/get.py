from requests import get
from jft.pickle.load_if_exists import f as load
from jft.dict.make_from_key_value_lists import f as make_from_key_value_lists

def f(name, response=None):
  response = response or get(f"https://pypi.org/project/{name}/")

  v_line = [l for l in response.text.split('\n') if all([
    '<h2>Initiate a new jft project</h2>' not in l,
    'jft ' in l,
    'title' not in l
  ])][0]

  v_str = v_line.split('jft ')[-1]
  
  return make_from_key_value_lists(
    ['major', 'minor', 'patch'],
    [int(_) for _ in v_str.split('.')]
  )

def t():
  observation = f("jft", response=load('./jft/pip/version/test_response.pkl')) 
  expectation = {'major': 0, 'minor': 0, 'patch': 4}
  test_passed = observation == expectation
  if not test_passed:
    print(f'test_passed: {test_passed}')
    print(f'observation: {observation}')
    print(f'expectation: {expectation}')
  return test_passed
