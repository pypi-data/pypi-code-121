from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdir
from jft.directory.exists import f as directory_exists

f = lambda directories: all([directory_exists(d) for d in directories])

root = './temp'
directories = [f'{root}/{directory}' for directory in ['abc', 'ghi', 'jkl']]
setup = lambda: [mkdirine(d) for d in [root, *directories]]
tear_down = lambda: rmdir(root)

def t():
  setup()
  expected_pass = f(directories)

  rmdir(root)
  expected_fail = f(directories)

  result = all([expected_pass, not expected_fail])

  tear_down()
  return result
