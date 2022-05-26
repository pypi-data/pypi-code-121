from jft.text_colours.bright.cyan import f as b_cyan
f = lambda μ: b_cyan(μ)
t = lambda: '\x1b[1;36mxyz\x1b[0;0m' == f('xyz')