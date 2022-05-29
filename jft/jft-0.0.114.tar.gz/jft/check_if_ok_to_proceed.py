from queue import Queue as Q

class FakeInput:
  def __init__(self, input_queue):
    self.q = Q()
    for item in input_queue:
      self.q.put(item)
  
  def __call__(self, prompt_text):
    return self.q.get()

def f(inp=input, silent=False):
  if silent: return 'silent'
  if inp("Safe to proceed? Enter 'n' to abort:") == 'n':
    raise RuntimeError('Something is wrong')

def test_proceed_path():
  fi = FakeInput(['y'])
  try:
    f(fi)
    return True
  except RuntimeError:
    return False

def test_do_not_proceed_path():
  fi = FakeInput(['n'])
  try:
    f(fi)
    return False
  except RuntimeError:
    return True

def test_silent():
  return f(silent=True) == 'silent'

t = lambda: all([
  test_proceed_path(),
  test_do_not_proceed_path(),
  test_silent()
])
