

def open(cls):
  def update(extension):
    namespace = dict(cls.__dict__)
    namespace.update(dict(extension.__dict__))
    return type(cls.__name__,cls.__bases__,namespace)
  return update

@open(str)
class Choice(object):
    pass