from subprocess import run as sprun
from jft.directory.make import f as mkdir
from jft.directory.remove import f as rmdir
from jft.text_colours.primary import f as primary

_root = '../temp_git_init'

def setup(): mkdir(_root)
def tear_down(): rmdir(_root)
args = ['git', 'init']
f = lambda cwd: sprun(cwd=cwd, capture_output=True, args=args)
def t():
  setup()
  z = f(_root)
  tear_down()
  return all([
    z.args==args,
    z.returncode==0,
    'Initialized empty Git repository in' in z.stdout.decode('utf-8'),
    not z.stderr.decode('utf-8')
  ])
