from ..curve_data import _tpl_curve_data


class _tpl_curve_generator:
  def __init__(self, c: _tpl_curve_data):
    self.curve = c

  def __create_table(self):
    table = f"\n  {'x':>8}, {'y':>8}"
    if self.curve.xerror is None and self.curve.yerror is None:
      table += "\n"
      table += "\n".join([f"  {cx:8}, {cy:8}" for cx, cy in zip(self.curve.x, self.curve.y)])
    elif self.curve.xerror is not None and self.curve.yerror is None:
      table += f", {'dx':>8}\n"
      table += "\n".join([
        f"  {cx:8}, {cy:8}, {cdx:8}"
        for cx, cy, cdx in zip(self.curve.x, self.curve.y, self.curve.xerror)
      ])
    elif self.curve.xerror is None and self.curve.yerror is not None:
      table += f", {'dy':>8}\n"
      table += "\n".join([
        f"  {cx:8}, {cy:8}, {cdy:8}"
        for cx, cy, cdy in zip(self.curve.x, self.curve.y, self.curve.yerror)
      ])
    elif self.curve.xerror is not None and self.curve.yerror is not None:
      table += f", {'dx':>8}, {'dy':>8}\n"
      table += "\n".join([
        f"  {cx:8}, {cy:8}, {cdx:8}, {cdy:8}"
        for cx, cy, cdx, cdy in zip(self.curve.x, self.curve.y, self.curve.xerror, self.curve.yerror)
      ])
    table += "\n"
    return table

  def _get_fill(self):
    return "%%fill"

  def _get_draw(self):
    return "%%draw"

  def _get_errdraw(self):
    return "%%draw"

  def _get_type(self):
    return "%%type (ybar, ybar interval)"

  def _get_marks(self):
    return "only marks,"

  def _get_legend_type(self):
    return "%%legend type (ybar legend)"

  def _get_errorstr(self, draw: bool = False):
    xerrorstr = "x dir=both,\n  x explicit," if self.curve.xerror is not None else "%x error options"
    yerrorstr = "y dir=both,\n  y explicit," if self.curve.yerror is not None else "%y error options"

    if self.curve.xerror is not None or self.curve.yerror is not None:
      errormarkstr = f"""  error mark options={{
    rotate=90,
    mark size=4pt,
    {self._get_errdraw()}
  }}"""
    else:
      errormarkstr = "  %error mark options"

    return '\n  '.join([xerrorstr, yerrorstr, errormarkstr])

  def _get_addplot_code(self):
    return f"""\\addplot+[
  {self.curve.color}
  {self._get_fill()}
  {self._get_draw()}
  {self._get_marks()}
  {"error bars/.cd," if self.curve.xerror is not None or self.curve.yerror is not None else "%error options"}
  {self._get_errorstr()}
  {self._get_type()}
  {self._get_legend_type()}
] table [
  x=x,
  {"x error=dx," if self.curve.xerror is not None else "%x error"}
  y=y,
  {"y error=dy," if self.curve.yerror is not None else "%y error"}
  col sep=comma
] {{{self.__create_table()}}};
{self.curve.label}
"""
