def f(x):
  x = x.replace('\ndef ', '\n\ndef ')
  x = x.replace('\n  def ', '\n\n  def ')
  return x

def t():
  expectation_0 = '\n\ndef '
  observation_0 = f('\ndef ')
  test_result_0 = expectation_0 == observation_0
  if not test_result_0:
    print(f'expectation: {expectation_0}')
    print(f'observation: {observation_0}')

  expectation_1 = '\n\n  def '
  observation_1 = f('\n  def ')
  test_result_1 = expectation_1 == observation_1
  if not test_result_1:
    print(f'expectation: {expectation_1}')
    print(f'observation: {observation_1}')

  expectation_2 = 'abc'
  observation_2 = f('abc')
  test_result_2 = expectation_2 == observation_2
  if not test_result_2:
    print(f'expectation: {expectation_2}')
    print(f'observation: {observation_2}')

  return all([
    test_result_0,
    test_result_1,
    test_result_2
  ])
