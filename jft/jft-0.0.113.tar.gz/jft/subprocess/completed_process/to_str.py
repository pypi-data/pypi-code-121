from subprocess import CompletedProcess
from jft.text_colours.primary import f as primary

f = lambda x: '\n'.join([
  f'{primary("x.args:")}{x.args}',
  '-'*80,
  f'{primary("x.returncode:")}{x.returncode}',
  '-'*80,
  f'{primary("x.stdout:")}\n{x.stdout.decode("utf-8")}',
  '-'*80,
  f'{primary("x.stderr:")}\n{x.stderr.decode("utf-8")}',
  '-'*80,
])

t = lambda: f(
  CompletedProcess(args=[], returncode=0, stdout=b'out', stderr=b'err')
) == '\n'.join([
  '\x1b[1;34mx.args:\x1b[0;0m[]',
  '-'*80,
  '\x1b[1;34mx.returncode:\x1b[0;0m0',
  '-'*80,
  '\x1b[1;34mx.stdout:\x1b[0;0m\nout',
  '-'*80,
  '\x1b[1;34mx.stderr:\x1b[0;0m\nerr',
  '-'*80
])
