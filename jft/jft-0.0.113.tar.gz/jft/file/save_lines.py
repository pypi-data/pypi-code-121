from os.path import exists
from os import remove
from os import mkdir
from jft.nop_x import f as nopx
from os import rmdir

def f(filepath, lines):
  with open(filepath, 'w') as _file:
    _file.writelines(lines)
  return lines

_filename = './_/temp.txt'

setup = lambda: (mkdir if not exists('_') else nopx)('_')

def tear_down():
  if exists(_filename):
    remove(_filename)
  rmdir('./_')

def t():
  setup()
  
  input_content = ['apple\n', 'banana\n', 'carrot\n']
  result = f(_filename, input_content)

  if not exists(_filename):
    print(f'{_filename} file was not created by file.write.run()')
    tear_down()
    return False

  with open(_filename, 'r') as _file:
    lines = _file.readlines()

  if lines != input_content:
    print(f'{lines} != {input_content}')
    tear_down()
    return False

  if result != input_content:
    print(f'{result} != {input_content}')
    tear_down()
    return False

  tear_down()
  return True
