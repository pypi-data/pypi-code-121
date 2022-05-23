from .curve_data import _tpl_curve_data
from .curve_generator.curve_generator import _tpl_curve_generator
from .curve_generator.ybar import _tpl_curve_generator_ybar, _tpl_curve_generator_ybarinterval


class _tpl_curve:
  def __init__(self, *args, **kwargs):
    self.__data = _tpl_curve_data(*args, **kwargs)
    self.__generator = _tpl_curve_generator(self.__data)

  def _set_plottype(self, type: str = 'xy'):
    gen_cls: _tpl_curve_generator = None
    if type == 'bar' or type == 'ybar' or type == 'hist' or type == 'histogram':
      gen_cls = _tpl_curve_generator_ybar
    elif type == 'interval' or type == 'ybar interval':
      gen_cls = _tpl_curve_generator_ybarinterval
    else:
      print(f"Cannot identify plottype \"{type}\". Keeping previous type (default: xy).")
      return
    self.__generator = gen_cls(self.__data)

  def _get_addplot_code(self):
    return self.__generator._get_addplot_code()
