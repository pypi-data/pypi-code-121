from jft.text_colours.bright.magenta import f as magenta
from jft.text_colours.bright.blue import f as blue
from jft.text_colours.bright.red import f as red
from jft.text_colours.bright.cyan import f as cyan
from jft.text_colours.bright.green import f as green

f = lambda w: {0: green, 1: cyan, 2: blue, 3: magenta, 4: red}[w//5]

t = lambda: all([
  *[green == f(_) for _ in range(5)],
  *[cyan == f(_) for _ in range(5, 10)],
  *[blue == f(_) for _ in range(10, 15)],
  *[magenta == f(_) for _ in range(15, 20)],
  *[red == f(_) for _ in range(20, 24)],
])