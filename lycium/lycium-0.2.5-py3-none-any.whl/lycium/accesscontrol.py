#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import tornado.gen
from bson import ObjectId
from IPy import IP
from .supports import singleton
from .utilities import tofloat
from .utilities.signatureutils import verify_inputs_data_sign_md5, verify_inputs_data_sign_hmac
from .asynchttphandler import args_as_dict, request_body_as_json
from .dbproxy import DbProxy

LOG = logging.getLogger('components.accesscontrol')

@singleton
class AccessControlManager(object):
    """
    """
    def __init__(self):
        self.white_list = {}
        self.black_list = {}
        self.signatures = {}
        self.applications = {}

    @tornado.gen.coroutine
    def reload_from_mongo(self, config_model):
        yield self.reload_access_limit_from_mongo(config_model)
        yield self.reload_signature_from_mongo(config_model)
        
    @tornado.gen.coroutine
    def reload_access_limit_from_mongo(self, config_model):
        db_proxy = DbProxy()
        limit = 100
        offset = 0
        last_id = None
        n = limit
        filters = {'type': 'access-limit', 'obsoleted': False}
        while n >= limit:
            n = 0
            if last_id:
                filters['id__gt'] = last_id
            LOG.info('loading app_config by %s from db offset:%d', filters['type'], offset)
            rows, total = yield db_proxy.query_list_mongo(config_model, filters, limit, 0, 'id', 'asc')
            for row in rows:
                n = n + 1
                last_id = ObjectId(row['id'])
                app_id = row.get('app_id')
                if not app_id:
                    continue
                opts = row.get('options')
                if not opts:
                    continue

                if app_id not in self.white_list:
                    self.white_list[app_id] = {}
                if app_id not in self.black_list:
                    self.black_list[app_id] = {}
                white_list = self.white_list[app_id]
                black_list = self.black_list[app_id]
                wl = opts.get('whitelist')
                bl = opts.get('blacklist')
                if wl:
                    for ip in wl:
                        try:
                            ipx = IP(ip)
                            for x in ipx:
                                white_list[str(x)] = True
                        except Exception as e:
                            LOG.warning('loading app_id:%s white list for ip:%s failed with error:%s', app_id, str(ip), str(e))
                    for ip in bl:
                        try:
                            ipx = IP(ip)
                            for x in ipx:
                                black_list[str(x)] = True
                        except Exception as e:
                            LOG.warning('loading app_id:%s black list for ip:%s failed with error:%s', app_id, str(ip), str(e))
            offset += n
        LOG.info('loading app_config by %s finished.', filters['type'])
        
    @tornado.gen.coroutine
    def reload_signature_from_mongo(self, config_model):
        db_proxy = DbProxy()
        limit = 100
        offset = 0
        last_id = None
        n = limit
        filters = {'type': 'signature', 'obsoleted': False}
        while n >= limit:
            n = 0
            if last_id:
                filters['id__gt'] = last_id
            LOG.info('loading app_config by %s from db offset:%d', filters['type'], offset)
            rows, total = yield db_proxy.query_list_mongo(config_model, filters, limit, 0, 'id', 'asc')
            for row in rows:
                n = n + 1
                last_id = ObjectId(row['id'])
                app_id = row.get('app_id')
                if not app_id:
                    continue

                if app_id not in self.signatures:
                    self.signatures[app_id] = {}
                signatures = self.signatures[app_id]
                signatures['signature_version'] = row.get('signature_version', '1.0')
                signatures['signature_field'] = row.get('signature_field', 'sign')
                signatures['signature_position'] = row.get('signature_position', 'body')
                signatures['signature_key'] = row.get('signature_key', '')
                signatures['expired_time'] = row.get('expired_time', 0)
            offset += n
        LOG.info('loading app_config by %s finished.', filters['type'])
        
    @tornado.gen.coroutine
    def reload_applications_from_mongo(self, application_model):
        db_proxy = DbProxy()
        limit = 100
        offset = 0
        last_id = None
        n = limit
        filters = {'type': '1910', 'obsoleted': False}
        while n >= limit:
            n = 0
            if last_id:
                filters['id__gt'] = last_id
            LOG.info('loading applications by %s from db offset:%d', filters['type'], offset)
            rows, total = yield db_proxy.query_list_mongo(application_model, filters, limit, 0, 'id', 'asc')
            for row in rows:
                n = n + 1
                last_id = ObjectId(row['id'])
                app_id = row.get('id')

                if app_id not in self.applications:
                    self.applications[app_id] = {}
                app_info = self.applications[app_id]
                app_info['name'] = row.get('name')
                app_info['type'] = row.get('type')
                app_info['code'] = row.get('code')
                app_info['cooperation_mode'] = row.get('cooperation_mode')
                app_info['expire_time'] = row.get('expire_time', 0)
                app_info['app_key'] = row.get('appKey')
        LOG.info('loading applications by %s finished.', filters['type'])
    
    def get_application_info(self, app_id):
        return self.applications.get(app_id, {})
    
    def get_signature_info(self, app_id):
        if app_id in self.signatures:
            return self.signatures[app_id]
        elif app_id in self.applications:
            return {
                'signature_version': '1.0',
                'signature_field': 'sign',
                'signature_position': 'body',
                'signature_key': self.applications[app_id]['app_key']
            }
        return False
        
ac_manager = AccessControlManager()

def whiteip_access_limit(request):
    app_id = request.headers.get('ApiAccessKey')
    if not app_id:
        LOG.warning('handled a request:%s and verifing whiteip access limit while api_access_key not given.', request.path)
        return False, 'Unknown access part'
    if app_id not in ac_manager.white_list:
        LOG.warning('handled a request:%s and verifing whiteip access limit while white list by app_id:%s not found.', request.path, str(app_id))
        return False, 'Access denied.'
    remote_ip = request.remote_ip
    if remote_ip not in ac_manager.white_list[app_id]:
        LOG.warning('handled a request:%s and verifing whiteip access limit while remote_ip:%s by app_id:%s not in white list.', request.path, str(remote_ip), str(app_id))
        return False, 'Access denied.'
    if app_id in ac_manager.black_list and remote_ip in ac_manager.black_list[app_id]:
        LOG.warning('handled a request:%s and verifing whiteip access limit while remote_ip:%s by app_id:%s in black list.', request.path, str(remote_ip), str(app_id))
        return False, 'Access denied.'
    return True, 'Success'

def signature_access_limit(request):
    app_id = request.headers.get('ApiAccessKey')
    if not app_id:
        LOG.warning('handled a request:%s and verifing signature access limit while api_access_key not given.', request.path)
        return False, 'Unknown access part'

    signature_info = ac_manager.get_signature_info(app_id)
    if not signature_info:
        LOG.warning('handled a request:%s and verifing signature access limit while signature by app_id:%s not found.', request.path, str(app_id))
        return False, 'Invalid api access key.'

    if signature_info.get('expired_time'):
        if time.time() > tofloat(signature_info.get('expired_time')):
            LOG.warning('handled a request:%s and verifing signature access limit while signature by app_id:%s not expired.', request.path, str(app_id))
            return False, 'Api expired.'

    params = None

    signature_version = signature_info.get('signature_version')
    signature_field = signature_info.get('signature_field')
    if signature_info.get('signature_position') == 'header':
        signature_value = request.headers.get(signature_field)
    else:
        if request.method == 'GET':
            params = args_as_dict(request)
        else:
            params = request_body_as_json(request)
        signature_value = params.get(signature_field)
    
    if not signature_value:
        LOG.warning('handled a request:%s and verifing signature access limit by app_id:%s while signature on field:%s in %s not filled.', request.path, str(app_id), signature_field, signature_info.get('signature_position'))
        return False, 'No signature part'
    if params is None:
        if request.method == 'GET':
            params = args_as_dict(request)
        else:
            params = request_body_as_json(request)
    if signature_version == '1.0':
        # md5
        verify_result = verify_inputs_data_sign_md5(signature_info.get('signature_key'), params, sign_field=signature_field, sign_value=signature_value)
        if not verify_result:
            LOG.warning('handled a request:%s and verifing signature access limit by app_id:%s while signature:%s on field:%s by md5 was invalid.', request.path, str(app_id), signature_value, signature_field)
            return False, 'Invalid signature part'
    elif signature_version == '2.0':
        # hmac
        verify_result = verify_inputs_data_sign_hmac(signature_info.get('signature_key'), params, sign_field=signature_field, sign_value=signature_value)
        if not verify_result:
            LOG.warning('handled a request:%s and verifing signature access limit by app_id:%s while signature:%s on field:%s by hmac was invalid.', request.path, str(app_id), signature_value, signature_field)
            return False, 'Invalid signature part'
    else:
        LOG.warning('handled a request:%s and verifing signature access limit by app_id:%s while signature by version:%s not supported.', request.path, str(app_id), signature_version)
        return False, 'Unknown configured signature version'
    
    return True, 'Success'

default_access_controls = [whiteip_access_limit, signature_access_limit]

def public_fields_control(request):
    params = None
    if params is None:
        if request.method == 'GET':
            params = args_as_dict(request)
        else:
            params = request_body_as_json(request)
    must_list = ["payload", "requestSn"]
    for ml in must_list:
        if not params.get(ml):
            return False, "lack %s." % ml
    return True, "success."

paltformaddition_access_controls = [public_fields_control]
