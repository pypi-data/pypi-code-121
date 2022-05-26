from jft.file.save import f as save
from jft.file.remove import f as remove
from jft.file.load import f as read_file
from jft.file.save_lines import f as apply_change_to_file
from jft.strings.make_patch_version_change_to_py import f as patch_setup_py

f = lambda version, filename: apply_change_to_file(
  filename,
  '\n'.join(patch_setup_py(version, read_file(filename).split('\n')))
)

filename='./fake_setup.py'
content = "\n".join([
  'from setuptools import setup',
  'from pathlib import Path',
  '',
  "setup(",
  "  name='jfti',",
  "  version='x.x.x',",
  "  description='Functional programming test driven development framework.',",
  "  long_description=Path('./README.md').read_text(),",
  "  long_description_content_type='text/markdown',",
  "  author='@JohnRForbes',",
  "  packages=['jfti']",
  ")",
])
version={'major': 1, 'minor': 2, 'patch': 3}

def setup(): save(filename, content)

def tear_down(): remove(filename)

def t():
  setup()
  f(version, filename)
  lines = read_file(filename).split('\n')
  version_line = [l for l in lines if l.startswith('  version=')][0]
  version_str = eval(version_line.strip()[:-1].split('=')[1])
  major, minor, patch = [int(_) for _ in version_str.split('.')]
  result = {'major': major, 'minor': minor, 'patch': patch} == version
  tear_down()
  return result
