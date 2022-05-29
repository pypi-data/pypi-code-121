f = lambda fn, body: '\n'.join([f'from _{fn} import f as {fn}', '', body])
t = lambda: (f('x', '#b')=='\n'.join(['from _x import f as x', '', '#b']))