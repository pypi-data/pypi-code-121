class Function:
  def __init__(self, name, text):
    self.name = name
    self.text = text

f = lambda name, text: Function(name, text)

def t():
  fn = f('abc', 'xyz')
  return all([fn.name == 'abc', fn.text == 'xyz'])
