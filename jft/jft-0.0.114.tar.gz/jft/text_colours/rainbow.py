from jft.text_colours.dark.red import f as d_red
from jft.text_colours.dark.green import f as d_green
from jft.text_colours.dark.yellow import f as d_yellow
from jft.text_colours.dark.blue import f as d_blue
from jft.text_colours.dark.magenta import f as d_magenta
from jft.text_colours.dark.cyan import f as d_cyan
from jft.text_colours.dark.white import f as d_white
from jft.text_colours.dark.default import f as d_default
from jft.text_colours.bright.red import f as b_red
from jft.text_colours.bright.yellow import f as b_yellow
from jft.text_colours.bright.green import f as b_green
from jft.text_colours.bright.cyan import f as b_cyan
from jft.text_colours.bright.blue import f as b_blue
from jft.text_colours.bright.magenta import f as b_mag
from jft.text_colours.bright.white import f as b_white

def f(μ):
  return '\n'.join([
    f'{(name+":"):<15} {fn(μ)}'
    for (name, fn)
    in [
      ('dark_red', d_red),
      ('dark_green', d_green),
      ('dark_yellow', d_yellow),
      ('dark_blue', d_blue),
      ('dark_magenta', d_magenta),
      ('dark_cyan', d_cyan),
      ('dark_white', d_white),
      ('default', d_default),
      ('bright_red', b_red),
      ('bright_yellow', b_yellow),
      ('bright_green', b_green),
      ('bright_cyan', b_cyan),
      ('bright_blue', b_blue),
      ('bright_magenta', b_mag),
      ('bright_white', b_white),
    ]
  ])

def t():
  return f('abc') == '\n'.join([
    f'{"dark_red:":<15} '+'\x1b[0;31mabc\x1b[0;0m',
    f'{"dark_green:":<15} '+'\x1b[0;32mabc\x1b[0;0m',
    f'{"dark_yellow:":<15} '+'\x1b[0;33mabc\x1b[0;0m',
    f'{"dark_blue:":<15} '+'\x1b[0;34mabc\x1b[0;0m',
    f'{"dark_magenta:":<15} '+'\x1b[0;35mabc\x1b[0;0m',
    f'{"dark_cyan:":<15} '+'\x1b[0;36mabc\x1b[0;0m',
    f'{"dark_white:":<15} '+'\x1b[0;37mabc\x1b[0;0m',
    f'{"default:":<15} '+'\x1b[0;39mabc\x1b[0;0m',
    f'{"bright_red:":<15} '+'\x1b[1;31mabc\x1b[0;0m',
    f'{"bright_yellow:":<15} '+'\x1b[1;33mabc\x1b[0;0m',
    f'{"bright_green:":<15} '+'\x1b[1;32mabc\x1b[0;0m',
    f'{"bright_cyan:":<15} '+'\x1b[1;36mabc\x1b[0;0m',
    f'{"bright_blue:":<15} '+'\x1b[1;34mabc\x1b[0;0m',
    f'{"bright_magenta:":<15} '+'\x1b[1;35mabc\x1b[0;0m',
    f'{"bright_white:":<15} '+'\x1b[1;37mabc\x1b[0;0m'
  ])
