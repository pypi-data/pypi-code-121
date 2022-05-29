f = lambda x: x.replace('\nrun = lambda self', '\n  run = lambda self')

t = lambda: '\n  run = lambda self' == f('\nrun = lambda self')