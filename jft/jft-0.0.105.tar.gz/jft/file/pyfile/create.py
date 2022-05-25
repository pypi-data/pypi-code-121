from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdir
from jft.file.load import f as load
from jft.file.remove import f as remove
from jft.file.save import f as save

_dirname = './temp'
_filename = f'{_dirname}/foo.py'
_data = '\n'.join(["f = lambda: None", "t = lambda: False", ""])

setup = lambda: mkdirine(_dirname)
tear_down = lambda: [remove(_filename), rmdir(_dirname)]
  
def t():
  setup()
  f(_filename, _data)
  observation = load(_filename)
  expectation = _data
  tear_down()
  return observation == expectation

def f(filename, data):
  return save(filename, data)

if __name__ == '__main__': f()
