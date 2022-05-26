from os.path import exists
from os import remove
from jft.file.save import f as save

def f(filepath):
  if exists(filepath):
    remove(filepath)
  return filepath

temp_file_path = './_.txt'

setup = lambda: save(temp_file_path, 'xyz')

def t():
  setup()
  z = f(temp_file_path)
  return all([not exists(temp_file_path), z == temp_file_path])
