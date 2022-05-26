from jft.text_colours.dark.yellow import f as d_yellow
f = lambda μ: d_yellow(μ)
t = lambda: '\x1b[0;33mxyz\x1b[0;0m' == f('xyz')