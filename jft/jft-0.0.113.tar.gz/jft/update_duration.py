def f(durations, name, δt_ms):
  durations[name] = (
    (durations[name] + δt_ms)/2
    if name
    in durations
    else δt_ms
  )
  return durations

def test_value_update():
  expectation = {'a': 0, 'b': 1.5}
  observation = f({'a': 0, 'b': 1}, 'b', 2)
  test_result = expectation == observation
  if not test_result:
    print('\n'.join([
      'Value update test failed',
      f'expectation: {expectation}',
      f'observation: {observation}',
    ]))
  return test_result

def test_value_create():
  expectation = {'a': 0, 'b': 1, 'c': 2}
  observation = f({'a': 0, 'b': 1}, 'c', 2)
  test_result = expectation == observation
  if not test_result:
    print('\n'.join([
      'Value create test failed',
      f'expectation: {expectation}',
      f'observation: {observation}',
    ]))
  return test_result

t = lambda: all([test_value_update(), test_value_create()])
