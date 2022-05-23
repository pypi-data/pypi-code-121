from collections.abc import Iterable
from .attribute import _tpl_attribute_function, _tpl_attribute_variable


class _tpl_curve_data:
  __counter: int = 0

  def __init__(self, x: Iterable, y: Iterable, xerror: Iterable = None, yerror: Iterable = None,
               label: str = None, color: str = None):
    self.x = x
    self.y = y
    self.xerror = xerror
    self.yerror = yerror
    self.label = _tpl_attribute_function(token="addlegendentry", value=label)
    self.tablename = "table%d" % self.__class__.__counter
    self.__class__.__counter += 1
    self.color = _tpl_attribute_variable(token="color", value=color)
