from zipfile import ZipFile
from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdirie
from jft.file.load import f as load

_dir = './temp_file_zip_extract'

setup = lambda: mkdirine(_dir)
tear_down = lambda: rmdirie(_dir)

def f(source, destination):
  with ZipFile(source, 'r') as _f:
    _f.extractall(destination)

def t():
  setup()
  f('./jft/file/zip/test_data.zip', _dir)
  expectation = load('./jft/file/zip/test_expectation.txt')
  observation = load(f'{_dir}/pi.txt')
  result = expectation == observation
  tear_down()
  return result
