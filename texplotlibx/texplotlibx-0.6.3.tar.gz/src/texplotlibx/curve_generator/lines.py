from .curve_generator import _tpl_curve_generator


class _tpl_curve_generator_lines(_tpl_curve_generator):
  def _get_draw(self):
    color = "=%s" % self.curve.color.get_value() if self.curve.color.get_value() is not None else ""
    return "draw%s,\n  draw opacity=0.7," % color
