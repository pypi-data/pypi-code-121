from jft.string.count_x_in_y import f as count_x_in_y

f = lambda x: all([
  ': return ' in x,
  'def ' in x,
  '(' in x,
  '):' in x,
  count_x_in_y('(', x) == count_x_in_y(')', x),
  count_x_in_y('[', x) == count_x_in_y(']', x),
  count_x_in_y('{', x) == count_x_in_y('}', x),
  count_x_in_y('"', x) % 2 == 0,
  count_x_in_y("'", x) % 2 == 0,
])

t = lambda: all([f('def t(): return False'), not f('def t():\nreturn False')])
