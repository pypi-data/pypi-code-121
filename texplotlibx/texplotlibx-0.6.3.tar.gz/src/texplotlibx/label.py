from .attribute import _tpl_attribute_variable


class _tpl_label:
  def __init__(self, text: str = None, token: str = None):
    self.text = _tpl_attribute_variable(token=token, value=text)
