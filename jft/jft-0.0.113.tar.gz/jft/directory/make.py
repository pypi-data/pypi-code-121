from os.path import exists
from os import mkdir
from re import L
from jft.nop_x import f as nop_x
from jft.directory.remove import f as remove

def f(x='./jft/classes'):
  if exists(x):
    return nop_x(x)
  try:
    mkdir(x)
  except FileNotFoundError as fe:
    f('/'.join(x.split('/')[:-1]))
    f(x)

temp_path_0 = './temp_dir_make'
temp_path_1 = f'{temp_path_0}/_'

def tear_down():
  remove(temp_path_1)
  remove(temp_path_0)

def t():
  f(x=temp_path_1)
  result = exists(temp_path_1)
  tear_down()
  if not result:
    print(f'Failed to create temporary directory: {temp_path_1}')
    return False
  return True