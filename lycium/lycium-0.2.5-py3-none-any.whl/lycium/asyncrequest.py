#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import urllib
import re
import http
import time
import traceback
import tornado.httpclient
import tornado.gen
import tornado.escape
from tornado.ioloop import IOLoop
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import Future, run_on_executor
import asyncio
import zeep
from .tornadozeep import TornadoAsyncTransport
from .exceptionreporter import ExceptionReporter

tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

logging.getLogger('tornado.curl_httpclient').setLevel(logging.WARN)
logging.getLogger('zeep.wsdl.wsdl').setLevel(logging.INFO)
logging.getLogger('zeep.xsd.schema').setLevel(logging.INFO)
logging.getLogger('zeep.transports').setLevel(logging.INFO)

LOG = logging.getLogger('async.request')

@tornado.gen.coroutine
def async_get(url, params=None, headers=None, verify_cert=True, **kwargs):
    response = yield async_http_request('GET', url, params, body=None, json=None, headers=headers, verify_cert=verify_cert, **kwargs)
    return response.code, response.body.decode()

@tornado.gen.coroutine
def async_get_bytes(url, params=None, headers=None, verify_cert=True, **kwargs):
    response = yield async_http_request('GET', url, params, body=None, json=None, headers=headers, verify_cert=verify_cert, **kwargs)
    return response.code, response.body

@tornado.gen.coroutine
def async_post(url, params=None, body='', json=None, headers=None, verify_cert=True, **kwargs):
    response = yield async_http_request('POST', url, params, body=body, json=json, headers=headers, verify_cert=verify_cert, **kwargs)
    return response.code, response.body.decode()

@tornado.gen.coroutine
def async_post_bytes(url, params=None, body='', json=None, headers=None, verify_cert=True, **kwargs):
    response = yield async_http_request('POST', url, params, body=body, json=json, headers=headers, verify_cert=verify_cert, **kwargs)
    return response.code, response.body

@tornado.gen.coroutine
def async_post_json(url, params=None, json=None, headers=None, verify_cert=True, **kwargs):
    response = yield async_http_request('POST', url, params, body=None, json=json, headers=headers, verify_cert=verify_cert, **kwargs)
    if response.code == http.HTTPStatus.OK:
        data = tornado.escape.json_decode(response.body.decode())
        return True, data
    res = str(response.reason) + ' ' + response.body.decode()
    return False, res

@tornado.gen.coroutine
def async_http_request(method, url, params=None, body='', json=None, headers=None, verify_cert=True, **kwargs):
    proxies = kwargs.pop('proxies', None)
    if params:
        qrs = [k + '=' + urllib.parse.quote(v) for k,v in params.items() ]
        sep = '&' if '?' in url else '?'
        url += sep + '&'.join(qrs)
    if json:
        body = tornado.escape.json_encode(json)
        if not headers:
            headers = {}
        headers['Content-Type'] = 'application/json'
    
    request = tornado.httpclient.HTTPRequest(url, method=method, body=body, headers=headers, validate_cert=verify_cert, **kwargs)
    client = tornado.httpclient.AsyncHTTPClient()
    prepare_request_proxies(request, proxies)
    
    response = yield client.fetch(request, raise_error=False)
    if response.code != http.HTTPStatus.OK:
        ExceptionReporter().report(key='HTTP-'+str(response.code), typ='HTTPQuery', 
            endpoint=url,
            method=method,
            inputs=body if body else tornado.escape.json_encode(params) if params else '',
            outputs=str(response.body.decode()),
            content=str(response.body.decode()),
            level='ERROR'
        )
    return response

def parse_http_proxies(proxy_url):
    '''parse http proxies from proxy url
    parse http://username:password@host:port as dict of schema://username:password@host:port
    '''
    if not proxy_url:
        return {}
    founds = re.search(r'(?P<schema>https?)://(?:(?P<username>[A-Za-z0-9\%\_\-\+\=]*)(?:\:(?P<password>[A-Za-z0-9\%\_\-\+\=]*))?\@)?(?P<host>(?:\w+)(?:\.\w+)*)(?:\:(?P<port>\d+))?', proxy_url)
    if not founds:
        return {}
    return {
        'schema': founds['schema'],
        'host': founds['host'],
        'port': int(founds['port'] if founds['port'] else 80),
        'username': urllib.parse.unquote(founds['username']) if founds['username'] else '',
        'password': urllib.parse.unquote(founds['password']) if founds['password'] else ''
    }

def prepare_request_proxies(request, proxies):
    if proxies:
        if 'host' in proxies and 'port' in proxies:
            request.proxy_host = proxies.get('host')
            request.proxy_port = int(proxies.get('port'))
        else:
            schema = 'http'
            if request.url.startswith('https'):
                schema = 'https'
            if schema in proxies:
                proxy_info = parse_http_proxies(proxies.get(schema))
                if proxy_info and proxy_info.get('host', False):
                    request.proxy_host = proxy_info.get('host', '')
                    request.proxy_port = int(proxy_info.get('port', 80))
                    if proxy_info.get('username', False):
                        request.proxy_username = proxy_info['username']
                    if proxy_info.get('password', False):
                        request.proxy_password = proxy_info['password']
        
# class AsyncSoapExecutor():
#     """
#     """
#     def __init__(self, ioloop = None):
#         # self.executor = ThreadPoolExecutor(max_workers=50)
#         # self.io_loop = ioloop or asyncio.new_event_loop()
#         pass

#     @tornado.gen.coroutine
#     def soap_request(self, future, endpoint, action, params, **kwargs):
#         proxies = kwargs.pop('proxies', None)
#         transport = kwargs.pop('transport', None)
#         uuid = kwargs.pop('uuid', None)
#         err = ''
#         context = ''
#         try:
#             web_client = zeep.AsyncClient(endpoint, transport=transport)
#             if not hasattr(web_client.service, action):
#                 return None, 'There is no action %s in wsdl %s' % (action, endpoint)
#             soap_method = web_client.service[action]
#             if isinstance(params, dict):
#                 context = yield soap_method(**params)
#             elif isinstance(params, list):
#                 context = yield soap_method(*params)
#             else:
#                 context = yield soap_method(params)
#         except Exception as e:
#             LOG.error(traceback.format_exc())
#             err = str(e)
#             ExceptionReporter().report(key='SOAP-'+str('failed'), typ='SOAPQuery', 
#                 endpoint=endpoint,
#                 method=str(action),
#                 inputs=str(params),
#                 outputs=str(context),
#                 content=err,
#                 level='ERROR'
#             )
#             # context = '{"code": -1, "message": %s}' % str(e)
#         if future:
#             future.set_result(context)
#         # print('result', context)
#         LOG.debug('%s %s %d response:\n%s', endpoint, action, uuid, context)
#         return context, err

class _wsdl_content(str):
    def __init__(self, endpoint: str) -> None:
        super().__init__()
        self.endpoint = endpoint
        self.content = bytes()
        self.expires = 0

    def read(self) -> bytes:
        return self.content

    def set_content(self, content: bytes) -> None:
        self.content = content
        self.expires = time.time() + 300

    def __str__(self) -> str:
        return self.endpoint

_wsdl_caches = {}

@tornado.gen.coroutine
def async_soap_request(endpoint, action, params, **kwargs):
    proxies = kwargs.pop('proxies', None)
    transport = kwargs.pop('transport', None)
    uuid = kwargs.pop('uuid', None)
    err = ''
    context = ''
    try:
        t1 = time.time()
        wsdl = None
        if endpoint in _wsdl_caches:
            wsdl = _wsdl_caches[endpoint]
            if wsdl.expires < t1:
                wsdl = None
        if wsdl is None:
            wsdl_code, wsdl_content = yield async_get_bytes(endpoint)
            if wsdl_code != 200:
                if wsdl_code == 301:
                    pass
                return None, 'Query wsdl %s failed with error:%s' % (endpoint, str(wsdl_content))
            wsdl = _wsdl_content(endpoint)
            wsdl.set_content(wsdl_content)
            _wsdl_caches[endpoint] = wsdl
        
        web_client = zeep.AsyncClient(wsdl, transport=transport)
        if not hasattr(web_client.service, action):
            return None, 'There is no action %s in wsdl %s' % (action, endpoint)
        soap_method = web_client.service[action]
        if isinstance(params, dict):
            context = yield soap_method(**params)
        elif isinstance(params, list):
            context = yield soap_method(*params)
        else:
            context = yield soap_method(params)
        ti = time.time() - t1
        if ti > 2:
            LOG.warning('query wsdl %s action %s cost too much time (%.2fs)', endpoint, action, ti)
    except Exception as e:
        LOG.error(traceback.format_exc())
        err = str(e)
        ExceptionReporter().report(key='SOAP-'+str('failed'), typ='SOAPQuery', 
            endpoint=endpoint,
            method=str(action),
            inputs=str(params),
            outputs=str(context),
            content=err,
            level='ERROR'
        )
        # context = '{"code": -1, "message": %s}' % str(e)
    # print('result', context)
    LOG.debug('%s %s response:\n%s', endpoint, action, context)
    return context, err

def main():
    import tornado.web
    from tornado.ioloop import IOLoop

    routes = [
    ]

    class GeneralTornadoHandler(tornado.web.RequestHandler):
        """
        """

        def initialize(self, callback, methods):
            self.callbacks = {}
            if isinstance(methods, str):
                methods = [methods]
            for method in methods:
                method = method.upper()
                self.callbacks[method] = callback

        @tornado.gen.coroutine
        def get(self):
            yield self._do_callback(self.callbacks.get('GET'))

        @tornado.gen.coroutine
        def post(self):
            yield self._do_callback(self.callbacks.get('POST'))
        
        @tornado.gen.coroutine
        def _do_callback(self, cb):
            if callable(cb):
                response = yield cb(self, self.request)
                if isinstance(response, str):
                    self.write(response)
                    self.finish()
                else:
                    print("====== response", response)
                    pass
            else:
                print('not callable cb:', cb)

    def tornado_route(rule, **options):
        def decorator(f):
            # endpoint = options.pop('endpoint', None)
            # if not endpoint:
            #     endpoint = f.__name__

            routes.append((rule, GeneralTornadoHandler, dict(callback=f, methods=options.pop('methods', ['GET']))))
            return f
        return decorator

    app2 = tornado.web.Application(routes)
    app2.listen(8021)
    
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
