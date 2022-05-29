from jft.string.hbar.make import f as hbar
from jft.string.header.python_file.make import f as make_py_filename_header
from jft.string.make_initial_content import f as make_initial_content
from jft.string.make_function_text import f as make_function_text
from jft.string.make_new_function_text import f as make_new_function_text
from jft.string.make_content_without_function import f as make_content_wo_func
from jft.terminal import Terminal

def f(π, silent=False, term=Terminal()):
  if silent: term.mode = 'test'
  term.clear()
  return term.print('\n'.join([
    hbar(),
    make_py_filename_header(π['π_filename']),
    make_initial_content(π['π_filename'], π['initial_content']),
    make_function_text(π['π_filename'], π['initial_function_text']),
    make_new_function_text(π['π_filename'], π['new_function_text']),
    make_content_wo_func(π['π_filename'], π['initial_other_text'])
  ]))

t = lambda: f({
  'π_filename': 'foo.py',
  'initial_content': 'abc',
  'initial_function_text': 'def ghi(): return 0',
  'new_function_text': 'def ghi(): return 1',
  'initial_other_text': 'blergh'
}, True)=='\n'.join([
  hbar(), '\x1b[1;36mpython_file:\x1b[0;0m foo.py',
  hbar('='), '\x1b[1;36mfoo.py initial_content:\x1b[0;0m', 'abc',
  hbar(), '\x1b[1;36mfoo.py function_text:\x1b[0;0m',
  'def ghi(): return 0',
  hbar(), '\x1b[1;36mfoo.py new_function_text:\x1b[0;0m',
  'def ghi(): return 1',
  hbar(), '\x1b[1;36mfoo.py content_without_function:\x1b[0;0m',
  'blergh',
  hbar()
])
