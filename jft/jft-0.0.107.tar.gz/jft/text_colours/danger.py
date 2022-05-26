from jft.text_colours.bright.red import f as red
f = lambda μ: red(μ)
t = lambda: f('flower') == '\x1b[1;31mflower\x1b[0;0m'
