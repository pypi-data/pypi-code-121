import pdb
from . import api_base
try:
    from StringIO import StringIO
except:
    from io import StringIO
import pandas as pd

from .. utils import convert_date
    
def event_brief(sort='time', pos=0, count=10, pandas=1):
    http_client = api_base.__get_conn__()
    request_string = []
    request_string.append('api/event/v1/brief')
    
    request_string.append('?sort=')
    request_string.append(str(sort))
    
    request_string.append('&pos=')
    request_string.append(str(pos))
    
    request_string.append('&count=')
    request_string.append(str(count))
    
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result

def event_detail(eid, pandas=1):
    http_client = api_base.__get_conn__()
    request_string = []
    request_string.append('api/event/v1/detail')
    
    request_string.append('?eid=')
    request_string.append(str(eid))
    result = api_base.__get_result__('GET',''.join(request_string), http_client, gw=True)
    return result