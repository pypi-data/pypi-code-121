import pdb
from . import api_base
try:
    from StringIO import StringIO
except:
    from io import StringIO
import pandas as pd
from .. utils import convert_date


def theme_brief(sort='time', pos=0, count=10, trade_date=None, pandas=1):
    http_client = api_base.__get_conn__()
    request_string = []
    request_string.append('api/theme/v1/brief')
    
    request_string.append('?sort=')
    request_string.append(str(sort))
    
    request_string.append('&pos=')
    request_string.append(str(pos))
    
    request_string.append('&count=')
    request_string.append(str(count))
    if trade_date is not None:
        request_string.append('&trade_date=')
        request_string.append(convert_date(trade_date))
    
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result

def theme_search(keyword, sort='heat', pandas=1):
    http_client = api_base.__get_conn__()
    request_string = []
    request_string.append('api/theme/v1/search')
    
    body={'keywords':str(keyword),'sort':str(sort)}
    result = api_base.__get_result__('POST',''.join(request_string), http_client, body, gw=True)
    return result
    
def theme_detail(tid, trade_date=None, pandas=1):
    http_client = api_base.__get_conn__()
    request_string = []
    request_string.append('api/theme/v1/detail')
    
    request_string.append('?tid=')
    request_string.append(str(tid))
    
    if trade_date is not None:
        request_string.append('&trade_date=')
        request_string.append(convert_date(trade_date))
    
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result