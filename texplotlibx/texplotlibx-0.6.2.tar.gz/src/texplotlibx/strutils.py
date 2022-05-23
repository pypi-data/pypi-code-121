def _compactify(s: str, level: int = 2):
  if level == 0:
    return s
  s = s.strip()
  if level == 1:
    return s
  s = "\n".join([x for x in s.split("\n") if x.strip() != ""])
  if level == 2:
    return s
  s = "\n".join([x for x in s.split("\n") if not x.strip().startswith("%")])
  if level == 3:
    return s


def _savetext(filename: str, text: str):
  with open(filename, "w") as f:
    f.writelines(text)


def _escape_characters(s: str, chars_to_escape: list[str] = None):
  if s is None:
    return s
  if chars_to_escape is None:
    chars_to_escape = ['%', '#']
  for ch in chars_to_escape:
    s = s.replace(ch, "\\" + ch)
  return s
