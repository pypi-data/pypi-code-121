from jft.pip.version.get import f as get_pip_version
from jft.pip.version.get import t as test_get_pip_version

from jft.setup.cfg.update import f as update_setup_cfg
from jft.setup.cfg.update import t as test_update_setup_cfg

from jft.setup.py.update import f as update_setup_py
from jft.setup.py.update import t as test_update_setup_py

from jft.pip.dist_tar.make import f as generate_new_dist_tar
from jft.pip.dist_tar.make import t as test_generate_new_dist_tar

from jft.system.git.commit.run import f as add_to_git
from jft.system.git.commit.run import t as test_add_to_git

from jft.pip.upload import f as start_upload
from jft.pip.upload import t as test_start_upload

from jft.directory.remove import f as rmdirie

from jft.file.save import f as save

from jft.pip.dist_tar.remove import f as remove_dist_tar
from jft.pip.dist_tar.remove import t as test_remove_dist_tar

from subprocess import run as sprun

temp_root = '..'
temp_dir_path = f'{temp_root}/jft_test'
temp_cfg_path = f'{temp_dir_path}/setup.cfg'
temp_py_path = f'{temp_dir_path}/setup.py'

def setup():
  _ = sprun(
    ['git', 'clone', 'git@gitlab.com:zereiji/jft_test.git'],
    cwd=temp_root,
    capture_output=True
  )

  save(temp_cfg_path, "\n".join([
    "[metadata]",
    "name = jft",
    "version = 1.2.3",
    "author = John Forbes",
    "author_email = john.robert.forbes@gmail.com",
    "description = Function Test Pair Toolbox",
    "long_description = file: README.md",
    "long_description_content_type = text/markdown",
    "url = https://gitlab.com/zereiji/jft",
    "license_files=LICENSE",
    "classifiers = ",
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
    "",
    "[options]",
    "packages = find:",
    "python_requires = >=3.7",
    "include_package_data = True",
  ]))

  save(temp_py_path, "\n".join([
    "from setuptools import setup",
    "from pathlib import Path",
    "long_description = Path('./README.md').read_text()",
    "",
    "setup(",
    "  name='jft',",
    "  version='1.2.4',",
    "  license='MIT',",
    "  description='Function Test Pair Toolbox',",
    "  long_description=long_description,",
    "  long_description_content_type='text/markdown',",
    "  author='@JohnRForbes',",
    "  author_email='john.robert.forbes@gmail.com',",
    "  url='https://gitlab.com/zereiji/jft',",
    "  packages=['jft'],",
    "  keywords='jft',",
    "  install_requires=[],",
    ")",
  ]))

def tear_down(): rmdirie(temp_dir_path)

def t():
  setup()
  observation = f(
    v={'major': 1, 'minor': 2, 'patch': 3},
    _root=temp_dir_path
  )
  expectation = {
    'v': {'major': 1, 'minor': 2, 'patch': 4},
    'cfg_path': '../jft_test/setup.cfg',
    'py_path': '../jft_test/setup.py'
  }
  passed = all([
    observation['v'] == expectation['v'],
    observation['cfg_path'] == expectation['cfg_path'],
    observation['py_path'] == expectation['py_path'],
    test_get_pip_version,
    test_update_setup_cfg,
    test_update_setup_py,
    test_remove_dist_tar,
    test_generate_new_dist_tar,
    test_add_to_git,
    test_start_upload,
  ])

  if not passed:
    print(f'observation: {observation}')
    print(f'expectation: {expectation}')

  tear_down()
  return passed

def f(v=None, _root='.'):
  cfg_path = f'{_root}/setup.cfg'
  py_path = f'{_root}/setup.py'

  v = v or get_pip_version('jft')
  v['patch'] += 1
  update_setup_cfg(v, cfg_path)
  update_setup_py(v, py_path)
  remove_dist_tar()
  generate_new_dist_tar(_root)
  add_to_git(cwd=_root, cap_out=True)
  upload_result = start_upload()

  result = {
    'v': v,
    'cfg_path': cfg_path,
    'py_path': py_path,
    'upload_result': upload_result
  } 

  return result
