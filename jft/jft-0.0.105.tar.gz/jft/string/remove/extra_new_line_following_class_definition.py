def f(content):
  class_lines = [
    line
    for line
    in content.split('\n')
    if all([line.startswith('class '), line.endswith(':'),])
  ]
  for class_line in class_lines:
    content = content.replace(class_line+'\n\n', class_line+'\n')
  return content

t = lambda: all([
  'class Foo:\ndef __init__(self):' == f('class Foo:\n\ndef __init__(self):'),
  'class Foo:\ndef __init__(self):' == f('class Foo:\ndef __init__(self):')
])