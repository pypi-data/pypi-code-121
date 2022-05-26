def f(content):
  lines = content.split('\n')
  lines_containing_import = [
    line
    for line
    in lines
    if any([
      all([
        'import' in line,
        line.startswith('from')
      ]),
      all([
        'import' in line,
        line.startswith('import')
      ])
    ])
  ]
  if lines_containing_import:
    final_line = lines_containing_import[-1]
    return content.replace(final_line, f'{final_line}\n')
  else:
    return content

def t():
  expectation_0 = 'from src.foo import run\n\nxyz'
  observation_1 = f('from src.foo import run\nxyz')
  test_result_0 = expectation_0 == observation_1

  expectation_1 = 'abc\nxyz'
  observation_1 = f('abc\nxyz')
  test_result_1 = expectation_1 == observation_1

  expectation_2 = 'abc\n\nxyz'
  observation_2 = f('abc\n\nxyz')
  test_result_2 = expectation_2 == observation_2

  return all([
    test_result_0,
    test_result_1,
    test_result_2
  ])