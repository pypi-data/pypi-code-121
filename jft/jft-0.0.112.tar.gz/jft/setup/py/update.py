from jft.file.load import f as load
from jft.file.save import f as save
from jft.strings.patch_setup_py import f as increment_patch_in_setup_py
from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdirie

temp_dir_path = temp_dir_path = './_setup_py_update'
temp_file_path = f'{temp_dir_path}/setup.py'

def setup():
  mkdirine(temp_dir_path)
  save(temp_file_path, "\n".join([
    "from setuptools import setup",
    "from pathlib import Path",
    "long_description = Path('./README.md').read_text()",
    "",
    "setup(",
    "  name='jft',",
    "  version='1.2.3',",
    "  license='MIT',",
    "  description='Function Test Pair Toolbox',",
    "  long_description=long_description,",
    '  long_description_content_type="text/markdown",',
    "  author='@JohnRForbes',",
    "  author_email='john.robert.forbes@gmail.com',",
    "  url='https://gitlab.com/zereiji/jft',",
    "  packages=['jft'],",
    "  keywords='jft',",
    "  install_requires=[],",
    ")",
  ]))

def tear_down(): rmdirie(temp_dir_path)

def f(v, filename='setup.py'):
  lines = load(filename).split('\n')
  new_lines = increment_patch_in_setup_py(v, lines)
  save(filename, "\n".join(new_lines))
  return None

def t():
  setup()
  f(v={'major': 4, 'minor': 5, 'patch': 6}, filename=temp_file_path)
  observation = load(temp_file_path)
  expectation = "version='4.5.6',"
  test_passed = expectation in observation
  if not test_passed:
    print(f'expectation: {expectation}')
    print(f'observation: {observation}')

  tear_down()
  return test_passed
