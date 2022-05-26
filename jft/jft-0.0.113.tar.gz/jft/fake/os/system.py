class FakeSystem:
  def __init__(self):
    self.history = []

  __call__ = lambda self, x: self.history.append(x)

  def reset(self):
    self.history = []

f = lambda: FakeSystem()

def t():
  fp = f()
  if fp.history != []: return False
  
  fp('boo')
  if fp.history != ['boo']: return False
  
  fp('bang')
  if fp.history != ['boo', 'bang']: return False
  
  fp.reset()
  if fp.history != []: return False

  return True
