from time import time
from jft.load_durations_if_exists import f as load_durations_if_exists
from jft.update_duration import f as update_duration
from jft.select_text_colour_from_width import f as select_colour_from_width
from jft.save_durations import f as save_durations
from jft.duration_bar import f as _duration_bar

def f(t_0, name, now=time):
  δt_ms = (now()-t_0)*1000
  durations = load_durations_if_exists()
  durations = update_duration(durations, name, δt_ms)
  save_durations(durations)
  dbar, w = _duration_bar(δt_ms)
  style = select_colour_from_width(w)
  return style(f'{dbar} {δt_ms:8.3f}')

fake_now = lambda: 0.0
t_0 = fake_now()

t = lambda: all([
  '\x1b[1;32m                           0.500\x1b[0;0m' == f(t_0-0.0005, 'abc', fake_now),
  '\x1b[1;32m                           1.000\x1b[0;0m' == f(t_0-0.001, 'abc', fake_now),
  '\x1b[1;32m█                          2.000\x1b[0;0m' == f(t_0-0.002, 'abc', fake_now),
  '\x1b[1;32m██                         4.000\x1b[0;0m' == f(t_0-0.004, 'abc', fake_now),
  '\x1b[1;32m███                        8.000\x1b[0;0m' == f(t_0-0.008, 'abc', fake_now),
  '\x1b[1;32m████                      16.000\x1b[0;0m' == f(t_0-0.016, 'abc', fake_now),
  '\x1b[1;36m█████                     32.000\x1b[0;0m' == f(t_0-0.032, 'abc', fake_now),
  '\x1b[1;36m██████                    64.000\x1b[0;0m' == f(t_0-0.064, 'abc', fake_now),
  '\x1b[1;36m███████                  128.000\x1b[0;0m' == f(t_0-0.128, 'abc', fake_now),
  '\x1b[1;36m████████                 256.000\x1b[0;0m' == f(t_0-0.256, 'abc', fake_now),
  '\x1b[1;36m█████████                512.000\x1b[0;0m' == f(t_0-0.512, 'abc', fake_now),
  '\x1b[1;34m██████████              1024.000\x1b[0;0m' == f(t_0-1.024, 'abc', fake_now),
  '\x1b[1;34m███████████             2048.000\x1b[0;0m' == f(t_0-2.048, 'abc', fake_now),
  '\x1b[1;34m████████████            4096.000\x1b[0;0m' == f(t_0-4.096, 'abc', fake_now),
  '\x1b[1;34m█████████████           8192.000\x1b[0;0m' == f(t_0-8.192, 'abc', fake_now),
  '\x1b[1;34m██████████████          16384.000\x1b[0;0m' == f(t_0-16.384, 'abc', fake_now),
  '\x1b[1;35m███████████████         32768.000\x1b[0;0m' == f(t_0-32.768, 'abc', fake_now),
  '\x1b[1;35m████████████████        65536.000\x1b[0;0m' == f(t_0-65.536, 'abc', fake_now),
  '\x1b[1;35m█████████████████       131072.000\x1b[0;0m' == f(t_0-131.072, 'abc', fake_now),
  '\x1b[1;35m██████████████████      262144.000\x1b[0;0m' == f(t_0-262.144, 'abc', fake_now),
  '\x1b[1;35m███████████████████     524288.000\x1b[0;0m' == f(t_0-524.288, 'abc', fake_now),
  '\x1b[1;31m████████████████████    1048576.000\x1b[0;0m' == f(t_0-1048.576, 'abc', fake_now),
  '\x1b[1;31m█████████████████████   2097152.000\x1b[0;0m' == f(t_0-2097.152, 'abc', fake_now),
  '\x1b[1;31m██████████████████████  4194304.000\x1b[0;0m' == f(t_0-4194.304, 'abc', fake_now),
  '\x1b[1;31m███████████████████████ 8388608.000\x1b[0;0m' == f(t_0-8388.608, 'abc', fake_now),
  '\x1b[1;31m███████████████████████ 16777216.000\x1b[0;0m' == f(t_0-16777.216, 'abc', fake_now),
])
