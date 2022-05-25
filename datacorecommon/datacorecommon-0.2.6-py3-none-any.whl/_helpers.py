# Dependencies
######################

# Type setting
######################

# Functions
######################


def _convert_to_list(_param):
  """
  Check the datatype of _param and change to a list if it is not yet a list.
  """
  if type(_param) != list:
    return [_param]
  else:
    return _param

def _assert_iso8601(param: str, format='%Y-%m-%d %H:%M:%S'):
    """
    Assert whether parameter is in ISO-8601 timestamp format
    Parameters
    ----------
    param : str
    format : str, optional
        The format which will be used in case the given input is a str object (default is %Y-%m-%d %H:%M:%S)
    """
    import re
    assert re.match('^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', param), f'Invalid timeformat found in {param}, format should be \'{format}\''