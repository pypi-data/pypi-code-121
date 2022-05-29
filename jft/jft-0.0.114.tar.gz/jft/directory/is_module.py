from os.path import exists
from os.path import isdir
from jft.directory.make import f as mkdirine
from jft.file.save import f as save
from jft.directory.remove import f as rmdirie

_dir = './_directory_is_module'

_dir_expected_true = f'{_dir}/_expected_true'
_dir_expected_false = f'{_dir}/_expected_false'

def setup():
  mkdirine(_dir)
  mkdirine(_dir_expected_true)
  save(f'{_dir_expected_true}/__init__.py', '')
  mkdirine(_dir_expected_false)

def tear_down(): rmdirie(_dir)

def f(x):
  return all([exists(x), isdir(x), exists(f'{x}/__init__.py')])

def t():
  setup()
  passed = all([f(_dir_expected_true), not f(_dir_expected_false)])
  tear_down()
  return passed