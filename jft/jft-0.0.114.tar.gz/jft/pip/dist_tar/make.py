from subprocess import run as sprun
from jft.text_colours.primary import f as primary
from jft.directory.remove import f as rmdir
from jft.directory.make import f as mkdir
from jft.file.save import f as save
from jft.file.zip.extract import f as extract

_root = '../temp'
base = './jft/system/git/commit'
setup_filepath = _root + '/setup.py'

f = lambda cwd='.': sprun(
  ['python3', 'setup.py', 'sdist'],
  cwd=cwd,
  capture_output=True
)

def setup():
  mkdir(_root)
  mkdir(_root+'/jft')
  save(_root+'/jft/__init__.py', '')
  extract(f'{base}/added_file_pre_commit.zip', '..')
  save(setup_filepath, "\n".join([
    'from setuptools import setup',
    'from pathlib import Path',
    '',
    "setup(",
    "  name='jft',",
    "  version='0.0.0',",
    "  description='Function Test Pair Toolbox',",
    "  long_description=Path('./README.md').read_text(),",
    "  long_description_content_type='text/markdown',",
    "  author='@JohnRForbes',",
    "  author_email='john.robert.forbes@gmail.com',",
    "  url='https://gitlab.com/zereiji/jft',",
    "  packages=['jft'],",
    "  classifiers=[",
    "    'Programming Language :: Python :: 3',",
    "    'License :: OSI Approved :: MIT License',",
    "    'Operating System :: OS Independent',",
    "  ],",
    '  python_requires=">=3.7",',
    "  include_package_data=True,",
    ")",
  ]))

tear_down = lambda: rmdir(_root)

def t():
  setup()
  z = f(_root)
  tear_down()
  return all([
    z.args == ['python3', 'setup.py', 'sdist'],
    z.returncode == 0,
    z.stdout.decode("utf-8") == '\n'.join([
      "running sdist",
      "running egg_info",
      "creating jft.egg-info",
      "writing jft.egg-info/PKG-INFO",
      "writing dependency_links to jft.egg-info/dependency_links.txt",
      "writing top-level names to jft.egg-info/top_level.txt",
      "writing manifest file 'jft.egg-info/SOURCES.txt'",
      "reading manifest file 'jft.egg-info/SOURCES.txt'",
      "writing manifest file 'jft.egg-info/SOURCES.txt'",
      "running check",
      "creating jft-0.0.0",
      "creating jft-0.0.0/jft",
      "creating jft-0.0.0/jft.egg-info",
      "copying files to jft-0.0.0...",
      "copying README.md -> jft-0.0.0",
      "copying setup.py -> jft-0.0.0",
      "copying jft/__init__.py -> jft-0.0.0/jft",
      "copying jft.egg-info/PKG-INFO -> jft-0.0.0/jft.egg-info",
      "copying jft.egg-info/SOURCES.txt -> jft-0.0.0/jft.egg-info",
      "copying jft.egg-info/dependency_links.txt -> jft-0.0.0/jft.egg-info",
      "copying jft.egg-info/top_level.txt -> jft-0.0.0/jft.egg-info",
      "Writing jft-0.0.0/setup.cfg",
      "creating dist",
      "Creating tar archive",
      "removing 'jft-0.0.0' (and everything under it)",
      "",
    ]),
    z.stderr.decode("utf-8") == ''
  ])