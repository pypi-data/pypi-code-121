from jft.file.save import f as save
from jft.file.load import f as load
from jft.file.remove import f as remove
from jft.file.decrypt import f as decrypt
from subprocess import run
from os.path import exists

_content = "Dyson Sphere\n"
_in_filename = "./_test_file_encrypt_in.txt"
_enc_filename = "./_test_file_encrypt_in.txt.enc"
_out_filename = "./_test_file_encrypt_out.txt"
_password = "goldilocks"

def f(in_filename, out_filename, password): run(
  args=[
    "openssl", "enc",
    "-aes-256-cbc",
    "-salt",
    "-pass", f"pass:{password}",
    "-in", f"{in_filename}",
    "-out", f"{out_filename}"
  ],
  capture_output=True
)

def setup():
  tear_down()
  save(_in_filename, _content)

def tear_down():
  remove(_in_filename)
  remove(_enc_filename)
  remove(_out_filename)

def t():
  setup()
  f(_in_filename, _enc_filename, _password)
  decrypt(_enc_filename, _out_filename, _password)
  observation = load(_out_filename)
  passed = observation == _content
  tear_down()
  return passed
