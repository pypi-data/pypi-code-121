f = lambda body: eval("lambda x: "+body.replace('\n', '\\n'))

test_x_squared = lambda: f("x*x")(2) == 4
test_newline_replacement = lambda: all([
  f("'\n\n' in x")('\n\n\n'), not f("'\n\n' in x")('abc')
])

test_newline_replacement_with_space = lambda: all([
  f("'\n \n' in x")('abc\n \n\nxyz'), not f("'\n \n' in x")('abc')
])

t = lambda: all([
  test_x_squared(),
  test_newline_replacement(),
  test_newline_replacement_with_space()
])