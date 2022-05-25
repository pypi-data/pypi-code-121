from re import split

def f(x):
  lines = x.split('\n')
  new_lines = []
  for index in range(len(lines)):
    if lines[index].strip().startswith('return '):
      previous_line = lines[index-1]
      
      return_line = lines[index]

      tokens_on_return_line = [
        _ for _ in split('=|<|>', return_line.replace('return ', '').strip())
        if len(_) > 0
      ]

      tokens_to_substitute = [
        token
        for token
        in tokens_on_return_line
        if token in previous_line
      ]

      if tokens_to_substitute:
        token_to_substitute = tokens_to_substitute[-1]
      else:
        return False, x

      token_value = previous_line.split('=')[-1]

      new_return_line = return_line.replace(token_to_substitute, token_value)
    
      new_lines.pop()
      new_lines.append(new_return_line)
    else:
      new_lines.append(lines[index])

  y = '\n'.join(new_lines)
  return len(x) > len(y), y

def t():
  x = '\n'.join([
    "f = lambda x: x*x",
    "def t():",
    "  y=f(4)",
    "  z=16",
    "  return y==z",
  ])
  change_made, y = f(x)
  z = '\n'.join([
    "f = lambda x: x*x",
    "def t():",
    "  y=f(4)",
    "  return y==16",
  ])
  return all([change_made, y == z])

if __name__ == '__main__': print(t())