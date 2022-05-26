from jft.string.remove.empty_lines import f as remove_empty_lines
from jft.text_colours.tgfr import f as tgfr

def f(content):
  first_def = content.find('def ')
  first_colon_following_first_def = content.find(':', first_def)
  second_def = content.find('def ', first_colon_following_first_def)
  _if_name_main = content.find("if __name__ == '__main__':")
  if first_def < 0:
    return ('', content)
  if second_def < 0:
    second_def = len(content)
  if _if_name_main < 0:
    _if_name_main = len(content)
  _min = min(second_def, _if_name_main)
  function_text = content[first_def: _min]
  other_text = remove_empty_lines(content[:first_def] + content[_min:])
  return (function_text, other_text)

_content = '\n'.join([
  "from x import run as x",
  "",
  "def default_equality_operator(y, z):",
  "  return y==z",
  "  # default_equality_operator = lambda y, z: y==z",
  "",
  "def f(π_filename):",
  "  initial_content = get_initial_content(π_filename)",
  "  ",
  "  (",
  "    initial_function_text,",
  "    initial_other_text",
  "  ) = separate_function_from_content(initial_content)",
  "",
  "  if not initial_function_text:",
  "    return",
  "",
  "  f_name, f_body = split_function_name_and_text(initial_function_text)",
  "  ",
  "  if function_is_ignorable(f_name):",
  "    return f_name",
  "  ",
  "  new_content = add_import_to_dismantled_content(f_name, initial_other_text)",
  "  new_function_text = 'def f'+f_body",
  "",
  "  show_proposed_dismantlement({",
  "    'π_filename': π_filename,",
  "    'initial_content': initial_content,",
  "    'new_content': new_content,",
  "    'initial_other_text': initial_other_text,",
  "    'initial_function_text': initial_function_text,",
  "    'new_function_text': new_function_text",
  "  })",
  "  check_if_ok_to_proceed()",
  "",
  "  write_function_to_file(f_name, new_function_text)",
  "  overwrite_existing_py_file(π_filename, new_content)",
])

_expectation_left = '\n'.join([
  "def default_equality_operator(y, z):",
  "  return y==z",
  "  # default_equality_operator = lambda y, z: y==z",
  "",
  "",
])

_expectation_right = '\n'.join([
  "from x import run as x",
  "",
  "def f(π_filename):",
  "  initial_content = get_initial_content(π_filename)",
  "  ",
  "  (",
  "    initial_function_text,",
  "    initial_other_text",
  "  ) = separate_function_from_content(initial_content)",
  "",
  "  if not initial_function_text:",
  "    return",
  "",
  "  f_name, f_body = split_function_name_and_text(initial_function_text)",
  "  ",
  "  if function_is_ignorable(f_name):",
  "    return f_name",
  "  ",
  "  new_content = add_import_to_dismantled_content(f_name, initial_other_text)",
  "  new_function_text = 'def f'+f_body",
  "",
  "  show_proposed_dismantlement({",
  "    'π_filename': π_filename,",
  "    'initial_content': initial_content,",
  "    'new_content': new_content,",
  "    'initial_other_text': initial_other_text,",
  "    'initial_function_text': initial_function_text,",
  "    'new_function_text': new_function_text",
  "  })",
  "  check_if_ok_to_proceed()",
  "",
  "  write_function_to_file(f_name, new_function_text)",
  "  overwrite_existing_py_file(π_filename, new_content)",
])

def t():
  observation_left, observation_right = f(_content)
  return all([
    observation_left == _expectation_left,
    observation_right == _expectation_right,
  ])

if __name__ == '__main__':
  print(f'Test passed: {tgfr(t())}')
  print('-'*18)
  observation_left, observation_right= f(_content)
  print(f'observation_left == expectation_left: {tgfr(observation_left == _expectation_left)}')
  if not observation_left == _expectation_left:
    observation_left_lines = observation_left.split('\n')
    expectation_left_lines = _expectation_left.split('\n')
    for index in range(len(observation_left_lines)):
      l = expectation_left_lines[index]
      r = observation_left_lines[index]
      if l != r:
        print(l)
        print(r)
        print()
  print(f'observation_right == expectation_right: {tgfr(observation_right == _expectation_right)}')
