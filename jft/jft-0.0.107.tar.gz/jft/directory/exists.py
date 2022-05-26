from os.path import exists
f = lambda directory: exists(directory)
t = lambda: f('.')
