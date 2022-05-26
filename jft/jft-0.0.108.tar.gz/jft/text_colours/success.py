from jft.text_colours.bright.green import f as b_green
f = lambda μ: b_green(μ)
t = lambda: '\x1b[1;32mxyz\x1b[0;0m' == f('xyz')