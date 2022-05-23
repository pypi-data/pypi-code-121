from .curve_generator import _tpl_curve_generator


class _tpl_curve_generator_ybar(_tpl_curve_generator):
  def _get_fill(self):
    color = "=%s" % self.curve.color.get_value() if self.curve.color.get_value() is not None else ""
    return "fill%s,\n  fill opacity=0.3," % color

  def _get_draw(self):
    color = "=%s" % self.ccurve.olor.get_value() if self.curve.color.get_value() is not None else ""
    return "draw%s,\n  draw opacity=0.7," % color

  def _get_errdraw(self):
    return self._get_draw()

  def _get_type(self):
    return "ybar,"

  def _get_marks(self):
    return "no marks,"

  def _get_legend_type(self):
    return "ybar legend,"


class _tpl_curve_generator_ybarinterval(_tpl_curve_generator_ybar):
  def _get_type(self):
      return "ybar interval,"
