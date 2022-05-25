from jft.file.load import f as load
from jft.string.separate_function_from_context import f as separate_function_from_content

from jft.directory.make import f as mkdir
from jft.directory.remove import f as rmdir
from jft.string.split_fn_name_and_text import f as split_function_name_and_text
from jft.file.save import f as save
from jft.string.fn_name.is_ignorable import f as function_is_ignorable
from jft.string.prepend_import import f as prepend_import
from jft.dict.proposed_dismantlement.show import f as show_proposed
from jft.check_if_ok_to_proceed import f as check_if_ok_to_proceed
from jft.function.write_to_file import f as write_function_to_file
from jft.function.function import Function

def f(π_filename, root='.', silent=True):
  initial_content = load(π_filename)

  (
    initial_function_text,
    initial_other_text
  ) = separate_function_from_content(initial_content)


  if not initial_function_text:
    return

  f_name, f_body = split_function_name_and_text(initial_function_text)

  if function_is_ignorable(f_name):
    return f_name


  new_content = prepend_import(f_name, initial_other_text)
  new_function_text = 'def f'+f_body

  show_proposed(
    {
      'π_filename': π_filename,
      'initial_content': initial_content,
      'new_content': new_content,
      'initial_other_text': initial_other_text,
      'initial_function_text': initial_function_text,
      'new_function_text': new_function_text
    },
    silent
  )

  check_if_ok_to_proceed(silent=silent)
  write_function_to_file(Function(name=f_name, text=new_function_text), root)
  save(π_filename, new_content)

_root = '../temp_pyfile_dismantle'
_π_filename = _root+'/foo.py'

def setup(): return [
  mkdir(_root),
  save(_π_filename, '\n'.join([
    '# Header comment',
    '',
    'def foo(x, y, z):',
    '  return x + y + z',
    '',
    'def goo(i, j):',
    '  return i * j',
    '',
    "if __name__ == '__main__':",
    '  print(foo(goo(1, 2), 3, 4))',
    ''
  ]))
]

def tear_down(): return [rmdir(_root)]

def t():
  setup()
  original_file_content = load(_π_filename)

  z = f(_π_filename, _root, silent=True)

  extracted_file_content = load( _root+'/_foo.py')
  updated_file_content = load(_π_filename)
  tear_down()
  return all([
    original_file_content != updated_file_content,
    extracted_file_content == '\n'.join([
      'def f(x, y, z):',
      '  return x + y + z',
      '',
      ''
    ]),
    updated_file_content == '\n'.join([
      'from _foo import f as foo',
      '',
      '# Header comment',
      '',
      'def goo(i, j):',
      '  return i * j',
      '',
      "if __name__ == '__main__':",
      '  print(foo(goo(1, 2), 3, 4))',
      ''
    ])
  ])