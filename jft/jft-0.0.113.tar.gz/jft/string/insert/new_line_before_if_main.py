f = lambda x: x.replace("\nif __name__ == '__ma", "\n\nif __name__ == '__ma")

def t():
  expectation_0 = "\n\nif __name__ == '__main__':"
  observation_1 = f("\nif __name__ == '__main__':")
  test_result_0 = expectation_0 == observation_1

  expectation_1 = 'abc\nxyz'
  observation_1 = f('abc\nxyz')
  test_result_1 = expectation_1 == observation_1

  return all([test_result_0, test_result_1])