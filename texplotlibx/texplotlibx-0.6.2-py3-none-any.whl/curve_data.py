from collections.abc import Iterable, Callable
from .attribute import _tpl_attribute_function, _tpl_attribute_variable


class _tpl_curve_data:
  __counter: int = 0

  @staticmethod
  def __sort(x: Iterable, y: Iterable, xerr: Iterable = None, yerr: Iterable = None):
    def __subsort(m: Iterable):
      return zip(*sorted(zip(*m)))
    if xerr is None and yerr is None:
      x, y = __subsort((x, y))
    elif xerr is None and yerr is not None:
      x, y, yerr = __subsort((x, y, yerr))
    elif xerr is not None and yerr is None:
      x, y, xerr = __subsort((x, y, xerr))
    else:
      x, y, xerr, yerr = __subsort((x, y, xerr, yerr))
    return x, y, xerr, yerr

  def __init__(self, x: Iterable, y: Iterable, xerror: Iterable = None, yerror: Iterable = None,
               label: str = None, color: str = None, yfunc: Callable = None, sortdata: bool = True):
    if yfunc is not None:
      y = map(yfunc, y)
      if yerror is not None:
        yerror = map(yfunc, yerror)
    self.x = x
    self.y = y
    self.xerror = xerror
    self.yerror = yerror

    if sortdata:
      self.x, self.y, self.xerror, self.yerror = self.__class__.__sort(self.x, self.y, self.xerror, self.yerror)

    self.label = _tpl_attribute_function(token="addlegendentry", value=label)
    self.tablename = "table%d" % self.__class__.__counter
    self.__class__.__counter += 1
    self.color = _tpl_attribute_variable(token="color", value=color)
