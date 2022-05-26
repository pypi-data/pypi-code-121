#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import logging
from .http_utils import url_query_json

LOG = logging.getLogger("utilities.restful_api")

def restful_get(uri, qry):
    params = urllib.parse.urlencode({'filter':json.dumps(qry)})
    ret, result = url_query_json(uri+'?'+params)
    if ret:
        LOG.info("query uri:%s succeed. result:%s", uri, str(result))
        return result
    else:
        LOG.error("query uri:%s failed with error:%s", uri, result)
        return ret

def restful_post(uri, data):
    ret, result = url_query_json(uri, data)
    if ret:
        LOG.info("post uri:%s succeed. result:%s", uri, str(result))
        return result
    else:
        LOG.error("post uri:%s failed with error:%s", uri, result)
        return ret
        
def restful_patch(uri, data, params={}):
    if params:
        params = urllib.parse.urlencode(params)
        uri = uri + '?' + params
    ret, result = url_query_json(uri, data, 'PATCH')
    if ret:
        LOG.info("query uri:%s with method:patch succeed. result:%s", uri, str(result))
        return result
    else:
        LOG.error("query uri:%s with method:patch failed with error:%s", uri, result)
        return ret
        