from jft.text_colours.danger import f as danger
f = lambda z: f'{z:3d}' if z else danger(f'{z:3d}')
t = lambda: all([f(0) == '\x1b[1;31m  0\x1b[0;0m', f(1) == '  1'])