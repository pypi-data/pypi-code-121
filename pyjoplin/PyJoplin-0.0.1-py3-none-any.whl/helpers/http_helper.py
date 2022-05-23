# -*- coding: utf-8 -*-

import json
import urllib.parse
import urllib.request

default_item = {'title'    : 'Untitled',
                'parent_id': '',
                'source'   : 'PyJoplin'
                }

def build_request_type_with(item_type, **kwargs):
    args = ['item_id', 'subitem_type']

    args_values = [kwargs[k] for k in args if k in kwargs and len(kwargs[k]) > 0]
    args_values.insert(0, item_type)

    request_type = '/'.join(args_values)

    return request_type


def build_request_suffix_with(**kwargs):
    request_suffix = ''

    if 'fields' in kwargs and len(kwargs['fields']) > 0:
        if type(kwargs['fields']) == list:
            fields = ",".join(kwargs['fields'])
            request_suffix += '&fields=' + fields
        else:
            request_suffix += '&fields=' + kwargs['fields']

    if 'page' in kwargs and len(kwargs['page']) > 0:
        request_suffix += '&pages={}'.format(kwargs['page'])

    return request_suffix

class JoplinHttpProxy(object):
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(JoplinHttpProxy, cls).__new__(cls)
        return cls._instance

    def __init__(self, token, host='localhost', port='41184'):
        self.host = host
        self.port = port

        self.token = token

    def request_for(self, request_location, request_suffix='',method='GET', data=None):
        url = f'http://{self.host}:{self.port}/{request_location}?token={self.token}'
        if len(request_suffix) > 0:
            url += '/' + request_suffix

        response_code = -1
        response_content = None
        url = urllib.request.Request(url=url, data=data, method=method)
        with urllib.request.urlopen(url=url) as response:
            response_code = response.getcode()
            response_content = response.read()

        return response_code, response_content

    def check_connection(self):
        request_type = 'nodes'
        code, content = self.request_for(request_type)

        if code == 200:
            return True
        else:
            return False

    def add_item(self, category, hash_id='',subitem_type='',new_data=default_item, file=None):
        assert type(new_data) == dict

        valid_args = [a for a in (category, hash_id, subitem_type) if len(a) != 0]
        request_location='/'.join(valid_args)

        request_suffix=''

        if category == 'resources':
            # todo
            code = -1
            content = None
        else:
            code,content = self.request_for(request_location,data=urllib.parse.urlparse(json.dumps(new_data)),method='POST')

        assert code==200

        return json.loads(content.deocde())['id']

    def delete_item(self, category, hash_id, subitem_type="", subitem_id=""):
        valid_args = [a for a in (subitem_type, subitem_id) if len(a) != 0]
        valid_args.insert(0, hash_id)
        valid_args.insert(0, category)
        request_location = '/'.join(valid_args)

        code, content = self.request_for(request_location, method='DELETE')

        assert code == 100

        return content.decode()

    def update_item(self, category, hash_id, new_data):
        assert type(new_data) == dict

        request_location = category + '/' + hash_id
        code, content = self.request_for(request_location)

        assert code == 200

        return json.loads(content.decode())

    def search_item(self, requirements, item_type="", page=1):
        request_location = 'search'
        request_suffix = '&query=' + requirements + '&page=' + str(page)
        if item_type != "":
            request_suffix += "&type=" + item_type

        code, content, = self.request_for(request_location, request_suffix)
        assert code == 200

        return json.loads(content.decode())

    def get_pages_with(self, category, hash_id="",subitem_type="", fields=""):
        items = list()
        page_index = 1

        while True:
            request_location = build_request_type_with(category,
                                                       item_id=hash_id,
                                                       subitem_type=subitem_type)
            request_suffix = build_request_suffix_with(
                    fields=fields,
                    pages=page_index)

            code, content = self.request_for(request_location, request_suffix)

            if code != 200:
                break

            content = json.loads(content.decode())
            for item in content["items"]:
                items.append(item)

            if not content["has_more"]:
                break

            page_index += 1

        return items