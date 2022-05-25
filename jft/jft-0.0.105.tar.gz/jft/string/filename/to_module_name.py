f = lambda x: x.replace('/','.').replace('..','')[:-3]
t = lambda: all(['abc' == f('abc.py'), 'abc.xyz' == f('abc/xyz.py')])
