from jft.text_colours.success import f as success
from time import time
from jft.file.remove import f as remove
from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdirie
from jft.pickle.save import f as save_pickle
from os.path import exists

_dir = './_handle_pass'
_failed_pickle_path = f'{_dir}/failed.pickle'

def setup():
  mkdirine(_dir)
  save_pickle({}, _failed_pickle_path)

def tear_down():
  rmdirie(_dir)

def t():
  setup()
  expectation = (True, '\x1b[1;32mPASS\x1b[0;0m 1000.00 ms. Tested: []')
  observation = f(0, [], 1)

  _failed_pickle_exists = exists(_failed_pickle_path)
  passed = all([
    expectation == observation,
    _failed_pickle_exists
  ])
  tear_down()
  return passed

def f(t_0, Π_to_test, t_now=None):
  t_now = t_now or time()

  remove('./failed.pickle')
  return (
    True,
    f"{success('PASS')} {1000*(t_now-t_0):0.2f} ms. Tested: {Π_to_test}"
  )