from jft.fake.printer import f as FP
def f(x, p=print): p(x); return False
def t():
  _fake_printer = FP()
  observation = f('abc', _fake_printer)
  expectation = False
  return all([
    _fake_printer.history[0] == 'abc',
    observation == expectation
  ])