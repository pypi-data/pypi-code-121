f = lambda content: '' if content == '\n' else content
t = lambda: all(['' == f('\n'), 'a\nz' == f('a\nz'), 'abc' == f('abc')])