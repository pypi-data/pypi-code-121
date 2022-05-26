#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import re
import tornado.gen
from components.asyncrequest import async_get_bytes

SKIP_HTTP_HEADERS = {
    'content-length': 1,
    'host': 1,
    'origin': 1,
    'referer': 1,
    'x-c-action': 1
}

def parse_static_urls(doc):
    urls = []
    r = re.findall(r'(?:href\=|src\=)[\"\']?([\/\w\.\d@_-]+(?:\.js|\.css))(?:[\"\']|[ \>]|\/\>)', doc)
    if r:
        for e in r:
            urls.append(str(e))
    return urls

def parse_css_file_urls(doc):
    urls = []
    r = re.findall(r'(?:url\()[\"\']?((?!data\:)[\/\w\.\d@_-]+)(?:[\"\'])?(?:(?:\#\w+)?\))', doc)
    if r:
        for e in r:
            urls.append(str(e))
    return urls

def parse_js_file_urls(doc):
    urls = []
    r = re.findall(r'[\"\']((?=static\/)[\/\w\.\d@_-]+)(?:[\"\'])', doc)
    if r:
        for e in r:
            urls.append(str(e))
    return urls

def parse_script_map_file_urls(doc, sub_path):
    urls = []
    r = re.findall(r'sourceMappingURL=([\w\d_\.]+(?:\.map))', doc)
    if r:
        for e in r:
            if sub_path:
                urls.append(os.path.join(sub_path, str(e)))
            else:
                urls.append(str(e))
    return urls

@tornado.gen.coroutine
def download_static_file_by_uri(uri, host, static_folder, proxies=None):
    head, fname = os.path.split(uri.strip('/'))
    if head.startswith('static/'):
        head = head[7:]
    save_path = os.path.join(static_folder, head)
    full_path = os.path.join(save_path, fname)
    if os.path.exists(full_path):
        return True
        
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    download_url = host + ('' if host.endswith('/') and uri.startswith('/') else '/') + uri
    try:
        http_code, result = yield async_get_bytes(download_url, verify_cert=False, proxies=proxies)
    except Exception as e:
        print("download file:%s failed with error:%s", uri, str(e))
        return False
    if http_code == 200:
        f = open(full_path, 'wb')
        f.write(result)
        f.close()

        result_text = result.decode()
        check_map_uris = False
        if fname.endswith('.js'):
            sub_uris = parse_js_file_urls(result_text)
            if sub_uris:
                yield [download_static_file_by_uri(f, host, static_folder, proxies=proxies) for f in sub_uris]
            check_map_uris = True
        elif fname.endswith('.css'):
            sub_uris = parse_css_file_urls(result_text)
            if sub_uris:
                yield [download_static_file_by_uri(f, host, static_folder, proxies=proxies) for f in sub_uris]
            check_map_uris = True
        if check_map_uris:
            sub_uris = parse_script_map_file_urls(result_text, head)
            if sub_uris:
                yield [download_static_file_by_uri(f, host, static_folder, proxies=proxies) for f in sub_uris]

        return True
    return False

@tornado.gen.coroutine
def download_static_files_by_uris(uris, host, static_folder, proxies=None):
    yield [ download_static_file_by_uri(uri, host, static_folder, proxies=proxies) for uri in uris]

def format_http_headers(srcheaders):
    headers = {}
    for k,v in srcheaders.items():
        chkkey = k.lower()
        if chkkey in SKIP_HTTP_HEADERS:
            continue
        headers[k] = v
    headers['Host'] = 'test-ssc.mohrss.gov.cn'
    return headers

if __name__ == '__main__':
    txt = """
    <!DOCTYPE html><html><head><meta charset=utf-8><meta name=apple-mobile-web-app-capable content=yes><meta name=apple-mobile-web-app-status-bar-style content=black><meta name=format-detection content="telephone=no, email=no"><meta name=msapplication-tap-highlight content=no><meta name=x5-orientation content=portrait><meta http-equiv=X-UA-Compatible content="IE=edge,chrome=1"><meta http-equiv=cache-control content=no-cache><meta http-equiv=expires content=0><meta http-equiv=Pragma content=no-cache><title></title><link href="/static/css/app.8651d5f4e43abcab5bbaf2a17a352a57.css" rel=stylesheet></head><body><div id=app></div><script type=text/javascript src='/static/js/manifest.2ae2e69a05c33dfc65f8.js'></script><script type=text/javascript src=/static/js/vendor.9800031b13afec2dda4f.js></script><script type=text/javascript src=/static/js/app.789ebb58cc3806382875.js></script></body></html>
    /*# sourceMappingURL=app.dd74c6d69cf48512be1aa5c6c1c951dc.css.map */
    """
    print(txt)
    print('===============================')
    urls = parse_static_urls(txt)
    print(urls)
    # for uri in urls:
    #     download_static_file_by_uri(uri, 'https://test-ssc.mohrss.gov.cn', 'web/static')
