from .attribute import _tpl_attribute_variable


class _tpl_logmodes:
  def __init__(self):
    self.x = _tpl_attribute_variable(token='xmode')
    self.y = _tpl_attribute_variable(token='ymode')

  def set_mode(self, mode: str):
    if mode == 'linear' or mode == '' or mode is None:
      self.x.set_value(None)
      self.y.set_value(None)
    if 'x' in mode:
      self.x.set_value('log')
    if 'y' in mode:
      self.y.set_value('log')
