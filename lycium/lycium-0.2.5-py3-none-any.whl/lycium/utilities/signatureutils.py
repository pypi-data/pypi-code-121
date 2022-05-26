#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import hashlib
import base64
import hmac
from . import md5_encode

def sign_inputs_data_md5(app_key, params, fields = None, sign_field = 'sign', sorted_fields = 1):
    """Signature the inputs data

    :app_key str Application signature key
    
    :params dict The inputs data in dict formation

    :fields list The field list that would be signatured, if attempts None, the fields would been taken params.keys()

    :sign_field str The field name that specifies signature data, this field name would be forcely skipped in params when formatting signature data.

    :sorted_fields int If > 0, the fields would be sorted increasely when formatting signature data, if < 0 the fields would be sorted reversely when formatting signature data.
    """

    if not fields:
        fields = [k for k in params.keys()]
    
    if sorted_fields > 0:
        fields.sort()
    elif sorted_fields < 0:
        fields.sort(reverse=True)

    signvalues = []
    for k in fields:
        if k == sign_field:
            continue
        signvalues.append(k + '=' + str(params.get(k, '')))
    
    signtext = '&'.join(signvalues) + app_key
    signdata = md5_encode(signtext)

    return signdata

def verify_inputs_data_sign_md5(app_key, params, fields = None, sign_field = 'sign', sorted_fields = 1, sign_value = ''):
    """Verify the signature data for inputs data

    :app_key str Application signature key
    
    :params dict The inputs data in dict formation

    :fields list The field list that would be signatured, if attempts None, the fields would been taken params.keys()

    :sign_field str The field name that specifies signature data, this field name would be forcely skipped in params when formatting signature data.

    :sorted_fields int If > 0, the fields would be sorted increasely when formatting signature data, if < 0 the fields would be sorted reversely when formatting signature data.
    """
    mysigndata = sign_inputs_data_md5(app_key, params, fields=fields, sign_field=sign_field, sorted_fields=sorted_fields)
    if not sign_value:
        sign_value = str(params.get(sign_field, ''))

    return sign_value == mysigndata

def sign_inputs_data_hmac(app_key, params, fields = None, sign_field = 'sign', sorted_fields = 1):
    """Signature the inputs data

    :app_key str Application signature key
    
    :params dict The inputs data in dict formation

    :fields list The field list that would be signatured, if attempts None, the fields would been taken params.keys()

    :sign_field str The field name that specifies signature data, this field name would be forcely skipped in params when formatting signature data.

    :sorted_fields int If > 0, the fields would be sorted increasely when formatting signature data, if < 0 the fields would be sorted reversely when formatting signature data.
    """

    if not fields:
        fields = [k for k in params.keys()]
    
    if sorted_fields > 0:
        fields.sort()
    elif sorted_fields < 0:
        fields.sort(reverse=True)

    signvalues = []
    for k in fields:
        if k == sign_field:
            continue
        signvalues.append(k + '=' + str(params.get(k, '')))
    
    signtext = '&'.join(signvalues)

    h = hmac.new(bytes(app_key, encoding='utf8'), digestmod=hashlib.sha1)
    h.update(bytes(signtext, encoding='utf8'))
    signdata = base64.b64encode(h.digest()).decode().rstrip()

    return signdata

def verify_inputs_data_sign_hmac(app_key, params, fields = None, sign_field = 'sign', sorted_fields = 1, sign_value = ''):
    """Verify the signature data for inputs data

    :app_key str Application signature key
    
    :params dict The inputs data in dict formation

    :fields list The field list that would be signatured, if attempts None, the fields would been taken params.keys()

    :sign_field str The field name that specifies signature data, this field name would be forcely skipped in params when formatting signature data.

    :sorted_fields int If > 0, the fields would be sorted increasely when formatting signature data, if < 0 the fields would be sorted reversely when formatting signature data.
    """
    mysigndata = sign_inputs_data_hmac(app_key, params, fields=fields, sign_field=sign_field, sorted_fields=sorted_fields)
    if not sign_value:
        sign_value = str(params.get(sign_field, ''))

    return sign_value == mysigndata
