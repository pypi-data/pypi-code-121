from os.path import exists
from os import remove
from os import mkdir
from jft.nop_x import f as nopx
from os import rmdir

def f(filepath, content):
  with open(filepath, 'w') as φ:
    φ.write(content)
    return content

_root = './temp_save_string'
_filepath = f'{_root}/temp.txt'

setup = lambda: (mkdir if not exists(_root) else nopx)(_root)

def tear_down():
  if exists(_filepath):
    remove(_filepath)
  rmdir(_root)

def t():
  setup()
  
  input_content = 'apple'
  result = f(_filepath, input_content)

  if not exists(_filepath):
    print(f'{_filepath} file was not created by file.write.run()')
    tear_down()
    return False

  with open(_filepath, 'r') as _file:
    file_content = _file.read()

  if file_content != input_content:
    print(f'{file_content} != {input_content}')
    tear_down()
    return False

  if result != input_content:
    print(f'{result} != {input_content}')
    tear_down()
    return False

  tear_down()
  return True
