f = lambda pyfiles, items: [p for p in pyfiles if p not in items]

t = lambda: all([
  [] == f([], []),
  ['./a.py', './b.py'] == f(
    ['./a.py', './b.py'],
    [
      './jft/jft.py',
      './jft/get_file_lines.py',
      './jft/terminal.py',
      './jft/refactor_recommender.py',
    ]
  ),
  ['./a.py', './b.py'] == f(
    ['./a.py', './jft/jft.py', './b.py'],
    [
      './jft/jft.py',
      './jft/get_file_lines.py',
      './jft/terminal.py',
      './jft/refactor_recommender.py',
    ]
  ),
  ['./a.py', './b.py'] == f(
    ['./a.py', './jft/get_file_lines.py', './b.py'],
    [
      './jft/jft.py',
      './jft/get_file_lines.py',
      './jft/terminal.py',
      './jft/refactor_recommender.py',
    ]
  ),
  ['./a.py', './b.py'] == f(
    ['./a.py', './jft/terminal.py', './b.py'],
    [
      './jft/jft.py',
      './jft/get_file_lines.py',
      './jft/terminal.py',
      './jft/refactor_recommender.py',
    ]
  ),
  ['./a.py', './b.py'] == f(
    [
      './a.py',
      './jft/refactor_recommender.py',
      './b.py'
    ],[
      './jft/jft.py',
      './jft/get_file_lines.py',
      './jft/terminal.py',
      './jft/refactor_recommender.py',
    ]
  ),
  ['./a.py', './b.py'] == f(
    [
      './a.py',
      './jft/jft.py',
      './jft/get_file_lines.py',
      './jft/terminal.py',
      './jft/refactor_recommender.py',
      './b.py'
    ],[
      './jft/jft.py',
      './jft/get_file_lines.py',
      './jft/terminal.py',
      './jft/refactor_recommender.py',
    ]
  )
])