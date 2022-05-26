from subprocess import run
from jft.directory.make import f as mkdirine
from jft.file.load import f as load
from jft.directory.remove import f as rmdirie

data = (
  b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03\xed\xd3\xe1\n\x820\x18\x85a/'
  b'\xc5+\xd0\xcd\xa6^\xce\x87\xd9\xa2\xa20\xb6\x05u\xf7)\x11T\x14\x8a\x85'
  b'\x11\xbd\xcf\x9f\x0f\xb6\xc16\x0e\'I%X\x1fd\xb1v\xb6\x0e\x8d;I\xdd\xec'
  b'\xf6\xcez/\xa1\x91P\xb9\xd47\x07W\xdb4\x1aO\xb5\xca2\xef\xa6.su;\xaf"m2'
  b'\xad\n\x95\x19\xdd\xae\xeb\xc2\xccL\x14\xe7o\xdc9\xd8\xc1\xb7\x9f\x8c\xe3h'
  b'\xd3s\xaeo\xffG%C\xf3\xaf\x92p\x0c\xe3\xee\xe8\x02.\n\xf3:\xffl\xf6\x90\x7f'
  b'\xd9\x8dX}\xf6\xab\xcf\xfdy\xfer\x89W\x96\xeb\xad\x95J\xf6UX}\xfbI\x98\xd0'
  b'\xe0\xfe\xcf\'\xee\xbf\xa6\xffS\xb8\xeb\xff\x9c\xfe\x03\x00\x00\x00\x00\x00'
  b'\x00\x00\x00\x00\x00\xf0\x8b\xce\xf3P\xde$\x00(\x00\x00'
)

_dir_name = './_test_tar_extract'
_archive_filename = f"compressed.tar.gz"
_archive_name = f'{_dir_name}/{_archive_filename}'
_expectation_dir_0 = f"{_dir_name}/_test_directory_compress_to_tar"
_expectation_dir_1 = f"{_expectation_dir_0}/source"


def setup():
  tear_down()
  mkdirine(_dir_name)
  with open(_archive_name, 'wb') as _file:
    _file.write(data)

def f(archive_filename, dir_name='.'):
  return run(
    args=f"tar -xvzf {archive_filename} -C {dir_name}".split(),
    capture_output=True
  )

def tear_down():
  rmdirie(_dir_name)
  rmdirie(_expectation_dir_0)

def t():
  setup()
  f(_archive_name, _dir_name)
  passed = all([
    load(f"{_expectation_dir_1}/a.txt") == '_source_file_a_path',
    load(f"{_expectation_dir_1}/b.txt") == '_source_file_b_path'
  ])
  tear_down()
  return passed
