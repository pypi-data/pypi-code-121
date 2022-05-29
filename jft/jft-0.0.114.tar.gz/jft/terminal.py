from jft.system.screen.clear import f as clear_screen

class Terminal:
  __init__ = lambda self, mode='run': self.reset(mode)

  def print(self, string:str=''):
    if self.mode == 'test':
      self.output_stream_as_list.append(string)
    else:
      print(string)
    return string

  def input(self, string=''):
    if self.mode == 'test':
      return self.input_stream_as_list.pop()
    else:
      return input(string)

  def reset(self, mode='run'):
    self.reset_stream_lists()
    self.mode = mode

  def reset_stdo(self): self.output_stream_as_list = []
  def reset_stdi(self): self.input_stream_as_list = []

  def reset_stream_lists(self):
    self.reset_stdi()
    self.reset_stdo()
  
  def clear(self, cls=None):
    self.reset_stdo()
    return (clear_screen if self.mode == 'run' else lambda: True)()

f = lambda mode='run': Terminal(mode)

def test_clear():
  terminal = f('test')
  terminal.print('abc')
  result = terminal.clear()
  return all([terminal.output_stream_as_list == [], result])

def test_terminal_print():
  terminal = f('test')
  data = 'abc'
  result = terminal.print(data)
  return all([terminal.output_stream_as_list == [data], result == data])

def test_terminal_input():
  terminal = f('test')
  terminal.input_stream_as_list.append('response text')
  returned_value = terminal.input('prompt text')
  return returned_value == 'response text'

def test_terminal_reset():
  terminal = f('test')

  terminal.mode = 'xyz'
  terminal.input_stream_as_list.append('abc')
  terminal.output_stream_as_list.append('ghi')
  terminal.reset()
      
  return all([
    terminal.mode == 'run',
    terminal.input_stream_as_list == [],
    terminal.output_stream_as_list == []
  ])

def test_terminal_reset_stdo():
  terminal = f('test')
  terminal.output_stream_as_list.append('ghi')
  terminal.reset_stdo()
  return terminal.output_stream_as_list == []

def test_terminal_reset_stdi():
  terminal = f('test')
  terminal.input_stream_as_list.append('ghi')
  terminal.reset_stdi()
  return terminal.input_stream_as_list == []

def test_terminal_reset_stream_lists():
  terminal = f('test')
  terminal.output_stream_as_list.append('abc')
  terminal.input_stream_as_list.append('ghi')
  terminal.reset_stream_lists()
  return all([
    terminal.output_stream_as_list == [],
    terminal.input_stream_as_list == []
  ])

t = lambda: all([
  test_terminal_print(),
  test_terminal_input(),
  test_terminal_reset(),
  test_terminal_reset_stdo(),
  test_terminal_reset_stdi(),
  test_terminal_reset_stream_lists(),
  test_clear()
])
