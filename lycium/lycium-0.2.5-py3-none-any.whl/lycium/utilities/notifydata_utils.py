#!/usr/bin/env python3.6
#! -*- coding: utf-8 -*-

import logging
import json
import http
import tornado.gen

from lycium.asyncrequest import async_post, async_soap_request
from utilities.xmlutil import parse_xml, format_xml
from utilities.signatureutils import sign_inputs_data_md5, sign_inputs_data_hmac

LOG = logging.getLogger('utilities.notifydata')

async def notify_data_to_peer_endpoint(endpoint, api_name, notify_data, signature_key, 
                                 signature_version='1.0', 
                                 signature_field='sign', 
                                 signature_position='body', 
                                 sign_fields=None, 
                                 serializing_type='JSON', 
                                 api_type='REST', 
                                 soap_port_name='QueryData', 
                                 soap_query_params=None,
                                 proxies=None):
    if signature_version == '1.0':
        sign = sign_inputs_data_md5(signature_key, notify_data, sign_fields, sign_field=signature_field)
    elif signature_version == '2.0':
        sign = sign_inputs_data_hmac(signature_key, notify_data, sign_fields, sign_field=signature_field)
    else:
        LOG.error('invalid peer signature version:%s for endpoint:%s', signature_version, endpoint + api_name)
        sign = sign_inputs_data_md5(signature_key, notify_data, sign_fields, sign_field=signature_field)
    
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
    }

    if signature_position == 'header':
        headers[signature_field] = sign
    else:
        if api_type != 'SOAP':
            notify_data[signature_field] = sign

    if serializing_type == 'JSON':
        query_body = json.dumps(notify_data)
    elif serializing_type == 'XML':
        headers['Content-Type'] = 'application/xml;charset=utf-8'
        query_body = format_xml(notify_data)
    else:
        return False, '商户系统配置不支持的数据序列化方式：' + serializing_type
    
    response_text = None
    if api_type == 'REST':
        http_code, response_text = await async_post(endpoint + api_name,
                                                    body=query_body,
                                                    headers=headers,
                                                    verify_cert=False,
                                                    proxies=proxies
                                                    )
        if http_code != http.HTTPStatus.OK:
            LOG.error('query %s failed with error_code:%d, %s', endpoint + api_name, http_code, response_text)
            return False, str(response_text)
        
    elif api_type == 'SOAP':
        soap_params = query_body
        if soap_query_params:
            if callable(soap_query_params):
                soap_params = soap_query_params(query_body, sign)
            else:
                soap_params = soap_query_params
        res, err = await async_soap_request(endpoint,
                                            soap_port_name,
                                            soap_params
                                            )
        if err:
            return False, err
        if isinstance(res, dict):
            if res.get('code') == 0:
                response_text = res.get('data')
            else:
                LOG.error('query %s failed with error:%s', endpoint + api_name, res.get('message'))
                return False, res.get('message')
        else:
            response_text = res
        
    else:
        return False, '未知的商户系统服务类型：' + api_type

    response_data = {}
    try:
        if serializing_type == 'JSON':
            response_data = json.loads(response_text)
        elif serializing_type == 'XML':
            response_data = parse_xml(response_text)
    except Exception as e:
        return False, '解析商户响应失败：' + str(e)
        
    return True, response_data
