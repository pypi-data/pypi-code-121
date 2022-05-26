from subprocess import run as sprun
from jft.strings.two_char_combinations import f as prepare_combinations

def f(original):
  data = original
  chars = ''.join(sorted(list(set(data))))
  Λ = prepare_combinations(chars)
  for λ in Λ:
    candidate_data = data.replace(λ, '')

    if len(candidate_data) < len(data):
      _raw_result = sprun(
        args=[ 'python3', '-c', candidate_data],
        capture_output=True
      )

      # print(f'_raw_result: {_raw_result}')
      _decoded_stdout = _raw_result.stdout.decode()
      # print(f'_decoded_stdout: {_decoded_stdout}')
      if len(_decoded_stdout) > 0:
        try:
          result = eval(_decoded_stdout)
        except SyntaxError as se:
          result = False

        if result:
          data = candidate_data

  return len(original)>len(data), data

def t():
  original_content = '\n'.join([
    "def foo(x):",
    "  return x*x",
    "",
    "def test():",
    "  expectation = 16",
    "  observation = foo(4)",
    "  return observation == expectation",
    "",
    "if __name__=='__main__':print(test())",
  ])
  change_made, z = f(original_content)
  return all([change_made, z=='\n'.join([
    "def o(x):",
    "  return x*x",
    "",
    "def tt():",
    "  pon = 16",
    "  n = o(4)",
    "  return n == pon",
    "",
    "if __name__=='__main__':print(tt())",
  ])])

if __name__=='__main__': print(t())