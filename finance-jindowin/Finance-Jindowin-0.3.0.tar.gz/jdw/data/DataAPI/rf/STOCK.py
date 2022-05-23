import pdb
from . import api_base
try:
    from StringIO import StringIO
except:
    from io import StringIO
import pandas as pd

from .. utils import convert_date


def stock_detail(code, pandas=1):
    http_client = api_base.__get_conn__()
    request_string = []
    request_string.append('api/stock/v1/detail')
    
    request_string.append('?code=')
    request_string.append(str(code))
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result