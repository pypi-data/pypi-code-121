f = lambda x: '@' in x
t = lambda: all([not f('abcdef'), f('abc@def')])