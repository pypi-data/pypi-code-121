from jft.string.filename.to_module_name import f as get_module_name

f = lambda py_filenames: sorted([get_module_name(f) for f in py_filenames])

t = lambda: all([
  [] == f([]),
  ['abc.xyz'] == f(['./abc/xyz.py']),
  ['abc.mno.xyz', 'abc.xyz'] == f(['./abc/xyz.py', './abc/mno/xyz.py']),
])