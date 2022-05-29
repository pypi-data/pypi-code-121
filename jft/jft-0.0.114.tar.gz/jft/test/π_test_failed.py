from importlib import import_module
from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdirie
from jft.file.save import f as save

_dir = './_π_test_failed'
_expected_pass_π_path = f'{_dir}/_expected_pass.py'
_expected_fail_π_path = f'{_dir}/_expected_fail.py'

def setup():
  mkdirine(_dir)
  save(_expected_pass_π_path, 'f = lambda: None\nt = lambda: True')
  save(_expected_fail_π_path, 'f = lambda: None\nt = lambda: False')

def tear_down(): rmdirie(_dir)

def f(π): return not import_module(π.replace('/','.').replace('..','')[:-3]).t()

def t():
  setup()
  passed = all([not f(_expected_pass_π_path), f(_expected_fail_π_path)])
  tear_down()
  return passed