from jft.directory.remove import f as rmdir
from os.path import exists
from subprocess import run as sprun
from jft.file.zip.extract import f as extract
from time import sleep as time_sleep
from jft.fake.sleep import f as fake_sleep

_dir_name = '../temp'
base = './jft/system/git/commit'

codes = {
  'A ': 'Added',
  'D ': 'Removed',
  'R ': 'Renamed',
  'M ': 'Modified',
}

def f(do_pull=True, cwd='.', do_push=True, cap_out=True, sleep=time_sleep):
  if do_pull:
    sprun(['git', 'pull'], cwd=cwd, capture_output=cap_out)
    sleep(0.05)

  sprun(['git', 'add', '-A'], cwd=cwd, capture_output=cap_out)
  sleep(0.05)

  short_git_status_output = sprun(
    ['git', 'status', '--short'],
    capture_output=cap_out,
    cwd=cwd
  )

  short_git_status_lines = [
    _
    for _
    in short_git_status_output.stdout.decode('utf-8').split('\n')
    if len(_)>0
  ]

  message = '  '.join([
    f'{codes[l]} {r}.'
    for (l, r)
    in [(_[:2], _[3:]) for _ in short_git_status_lines]
  ])

  sprun(['git', 'commit', '-m', message], capture_output=cap_out, cwd=cwd)
  sleep(0.05)
  
  if do_push:
    sprun(['git', 'push'], cwd=cwd, capture_output=False)
    sleep(0.05)

setup_added = lambda: extract(f'{base}/added_file_pre_commit.zip', '..')
setup_deleted = lambda: extract(f'{base}/deleted_file_pre_commit.zip', '..')
setup_renamed = lambda: extract(f'{base}/renamed_file_pre_commit.zip', '..')
setup_modified = lambda: extract(f'{base}/modified_file_pre_commit.zip', '..')
tear_down = lambda: rmdir(_dir_name)

observe = lambda: sprun(
  ['git', 'log', '--pretty=oneline'],
  capture_output=True,
  cwd=_dir_name
).stdout.decode('utf-8').split('\n')[0][41:]

def test_added():
  setup_added()
  f(do_pull=False, do_push=False, sleep=fake_sleep, cwd=_dir_name)
  expectation = 'Added foo.py.'
  observation = observe()
  result = expectation == observation
  tear_down()
  return result

def test_deleted():
  setup_deleted()
  f(do_pull=False, do_push=False, sleep=fake_sleep, cwd=_dir_name)
  expectation = 'Removed README.md.'
  observation = observe()
  result = expectation == observation
  tear_down()
  return result

def test_renamed():
  setup_renamed()
  f(do_pull=False, do_push=False, sleep=fake_sleep, cwd=_dir_name)
  expectation = 'Renamed README.md -> renamed_readme.md.'
  observation = observe()
  result = expectation == observation
  tear_down()
  return result

def test_modified():
  setup_modified()
  f(do_pull=False, do_push=False, sleep=fake_sleep, cwd=_dir_name)
  expectation = 'Modified README.md.'
  observation = observe()
  result = expectation == observation
  tear_down()
  return result

def t():
  if exists(_dir_name): tear_down()
  return all([test_added(), test_deleted(), test_renamed(), test_modified()])
