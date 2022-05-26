from jft.directory.list_pyfilepaths import f as list_py_files
from jft.directory.make import f as mkdir
from jft.file.save import f as save
from os import remove
from jft.directory.remove import f as remove_dir

f = lambda root='.': [
  φ for φ in list_py_files(root, [])
  if not any([
    φ in [
      './scrap.py',
      './patch.py',
      './test.py',
      './setup.py',
      './temp.py',
      './temp/foo.py',
      './temp/jft.args.py',
      './temp/jft.start.py',
      './temp/jft.app.py',
      './temp/jft.no_comment_present.py',
      './temp/jft.has_comment_to_be_deleted.py',
      './temp/jft.has_comment_to_not_be_deleted.py',
      './fake_setup.py',
      './_π_test_failed/_expected_fail.py',
      './_π_test_failed/_expected_pass.py',
      './package_list.py'
    ],
    φ.endswith('__init__.py'),
    φ.endswith('data.py')
  ])
]

temp_dir_0 = './_'
temp_dir_1 = './_/_'
temp_files_and_content = [
  (f'{temp_dir_0}/foo.py', 'f = lambda: None\nt = lambda: True'),
  (f'{temp_dir_0}/xyz.txt', 'xyz'),
  (f'{temp_dir_1}/abc.txt', 'abc'),
  (f'{temp_dir_1}/bar.py', 'f = lambda: None\nt = lambda: True'),
]

def setup():
  [mkdir(temp_dir) for temp_dir in [temp_dir_0, temp_dir_1]]
  [save(filename, content) for (filename, content) in temp_files_and_content]

def tear_down():
  [remove(filename) for (filename, _) in temp_files_and_content]
  remove_dir(temp_dir_1)
  remove_dir(temp_dir_0)

def t():
  setup()
  expectation = set([
    './_/_/bar.py',
    './_/foo.py'
  ])
  observation = set(f(temp_dir_0))
  test_result = expectation == observation
  tear_down()

  if not test_result:
    print(f'expectation: {expectation}')
    print(f'observation: {observation}')

  return test_result