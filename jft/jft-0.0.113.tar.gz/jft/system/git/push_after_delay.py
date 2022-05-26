from subprocess import run as sprun
from time import sleep
from time import time

def f(delay_s=5):
  sleep(delay_s)
  return sprun(['git', 'push'], capture_output=True)

def t():
  delay_s = 0.5
  t_margin_min, t_margin_max = 2.0, 4.0

  t_0 = time()
  y = f(delay_s)
  t_1 = time()
  duration = t_1 - t_0

  command_sent_ok = all([
    ' '.join(y.args) == 'git push',
    y.stderr.decode('utf-8') == 'Everything up-to-date\n'
  ])

  if duration < (delay_s + t_margin_min):
    print(''.join([
      f'Function execution duration: {duration:0.5f} did not satisfy minimum',
      f' duration: {delay_s} + {+ t_margin_min} [s].'
    ]))
    return False

  if duration > (delay_s*2 + t_margin_max):
    print(''.join([
      f'Function was too slow: {duration:0.5f} > {delay_s}×2 + {t_margin_max}.'
    ]))
    return False
  return command_sent_ok
