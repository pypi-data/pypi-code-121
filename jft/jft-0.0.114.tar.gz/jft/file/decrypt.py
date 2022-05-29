from jft.file.load import f as load
from jft.file.remove import f as remove
from subprocess import run

_in_filepath = "_test_file_decrypt.txt.enc"
_out_filepath = "_test_file_decrypt.txt"

def f(in_filepath, out_filepath, password):
  run(args=[
    "openssl",
    "enc",
    "-aes-256-cbc",
    "-pass",
    f"pass:{password}",
    "-d",
    "-in", in_filepath,
    "-out", out_filepath
  ], capture_output=True)

def setup():
  tear_down()
  with open(_in_filepath, 'wb') as _file:
    _file.write(
      b'Salted__\xb1$\xae\xb31h\x04\xd7'
      b'\xbc\x7fq\xe2\xb5\x07\x04wJ\xe6\xc4\xd4\xcb[{^'
    )

def tear_down():
  remove(_in_filepath)
  remove(_out_filepath)

def t():
  setup()
  f(_in_filepath, _out_filepath, 'abcd1234')
  passed = load(_out_filepath) == 'abc123'
  tear_down()
  return passed
