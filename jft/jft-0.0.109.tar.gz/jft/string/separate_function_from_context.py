from jft.string.remove.empty_lines import f as remove_empty_lines

def f(content):
  first_def = content.find('def ')
  if first_def < 0:
    return ('', content)

  second_def = content.find('def ', first_def+1)
  if second_def < 0:
    second_def = len(content)

  _if_name_main = content.find("if __name__ == '__main__':")
  if _if_name_main < 0:
    _if_name_main = len(content)

  _min = min(second_def, _if_name_main)

  function_text = content[first_def: _min]
  other_text = remove_empty_lines(content[:first_def] + content[_min:])

  return (function_text, other_text)

_test_content = '\n'.join([
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

def t():
  z = f(_test_content)
  function_text, other_text = z

  return all([
    function_text == '\n'.join([
      "def default_equality_operator(y, z):",
      "  return y==z",
      "  # default_equality_operator = lambda y, z: y==z",
      "",
      ""
    ]),
    other_text == '\n'.join([
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
  ])
