from subprocess import run as sprun
from jft.fake.subprocess.run import f as fake_sprun
from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdirie
from jft.file.load import f as load

_dir = '../start_upload'

def setup(): return mkdirine(_dir)
def tear_down(): return rmdirie(_dir)

_username = load('username.secret')
_password = load('password.secret')

def f(sprun=sprun, cwd='.', capture_output=True):
  return sprun(
    ['twine', 'upload', 'dist/*', '-u', _username, '-p', _password],
    cwd=cwd,
    capture_output=capture_output
  )

def t():
  setup()
  observation = f(fake_sprun, cwd=_dir)
  result = all([
    _password in observation.args,
    _username in observation.args,
    'twine' in observation.args,
    'upload' in observation.args,
    'dist/*' in observation.args,
    '-u' in observation.args,
    '-p' in observation.args,
    observation.returncode == 0,
    'Uploading distributions to https://upload.pypi.org' in observation.stdout.decode()
  ])
  tear_down()
  return result
