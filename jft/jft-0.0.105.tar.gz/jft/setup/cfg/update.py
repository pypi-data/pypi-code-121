from jft.file.load import f as load
from jft.file.save import f as save
from jft.strings.patch_setup_cfg import f as increment_patch_in_setup_cfg
from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdirie

temp_dir_path = temp_dir_path = './_setup_cfg_update'
temp_file_path = f'{temp_dir_path}/setup.cfg'

def setup():
  mkdirine(temp_dir_path)
  save(temp_file_path, "\n".join([
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

def tear_down():
  rmdirie(temp_dir_path)

def f(v, filename='setup.cfg'):
  lines = load(filename).split('\n')
  new_lines = increment_patch_in_setup_cfg(v, lines)
  save(filename, "\n".join(new_lines))
  return None

def t():
  setup()
  f(v={'major': 4, 'minor': 5, 'patch': 6}, filename=temp_file_path)
  observation = load(temp_file_path)
  test_passed = "version = 4.5.6" in observation
  tear_down()
  return test_passed
