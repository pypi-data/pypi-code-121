from jft.function.function import Function
from jft.file.save import f as save
from jft.file.remove import f as remove
from jft.file.load import f as load

f = lambda fn, root='.': save(f'{root}/_{fn.name}.py', fn.text)

_filepath = './_foo.py'

tear_down = lambda: remove(_filepath)

def t():
  fn = Function('foo', 'run = lambda: "foo"\ntest = lambda: "foo" == run()')
  f(fn)
  content = load(_filepath)
  test_result = content == fn.text
  tear_down()
  return test_result
