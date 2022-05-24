from io import StringIO

class Packages(list):
  def __init__(self):
    list.__init__(self)

  def __str__(self):
    buffer = StringIO()

    for i, package in enumerate(self):
      if i: buffer.write('\n')
      buffer.write(str(package))
    string = buffer.getvalue()
    buffer.close()
    return string
