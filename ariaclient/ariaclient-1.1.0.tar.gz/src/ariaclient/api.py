import logging, base64, io
import requests
import shutil
import mimetypes
from lxml import etree
import json
import pathlib


class AriaService:
    def __init__(self, base_url, cert_file, session_id, **kwargs):
        self._base_url = base_url
        self._certificate = AriaService.read_cert(cert_file)
        self._token = None
        self._session_id = session_id
        self._timeout_default = 30 if 'timeout' not in kwargs else int(kwargs['timeout'])
        app_cert_file = None if 'app_credentials' not in kwargs  else kwargs['app_credentials']
        self._app_credentials = None if app_cert_file is None else AriaService.read_cert(app_cert_file)
        self._headers = {}

    def _process_aria_message(self, res, attribute=None):
        try:
            data = res.json()           #raises a ValueError if no valid json returned
            if attribute is None:
                if 'messages' in data:
                    return data['messages']
                elif 'message' in data:
                    return data['message']
                else:
                    raise AriaError('No {} returned from server'.format(attribute), res)
            elif attribute in data:
                return data[attribute]
            else:
                raise AriaError('Unrecognised server response', res)
        except ValueError as ve:
            raise AriaError(ve.args[0], res)

    def authenticate(self):
        data = {
            "session": self._session_id,
            "credentials": self._certificate.decode('utf-8')
        }
        if self._app_credentials is not None:
            data['appCredentials'] = self._app_credentials.decode('utf-8')
        res = requests.post(
            self._base_url+'/auth',
            json=data,
            headers={'content-type': 'application/json'}
        )
        res.raise_for_status()
        token = self._process_aria_message(res, 'token')
        self._headers['Authorization'] = 'Bearer {}'.format(token)

    def get_messages(self):
        res = requests.get(
            self._base_url+'/message',
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    def search_messages(self, data, timeout=None, limit=1000):
        timeout = self._timeout_default if timeout is None else timeout

        res = requests.post(
            self._base_url+'/message/search',
            json=data,
            headers=self._headers,
            timeout=timeout,
            params={'limit': limit}
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    def send_message(self, channel, message, **kwargs):
        payload = {"channel": channel,
                       "options": {
                           'disableEncoding': None if 'disableEncoding' not in kwargs else kwargs['disableEncoding'],
                           'passthrough': None if 'passthrough' not in kwargs else kwargs['passthrough']
                       }
                   }
        data = None if 'data' not in kwargs else kwargs['data']
        if isinstance(data, str):
            data = json.loads(data)
        payload = AriaService.set_text(payload, message, data)
        if 'attachment' in kwargs and kwargs['attachment'] is not None:
            if isinstance(kwargs['attachment'], tuple):
                filename, fdata = kwargs['attachment']
                payload['attachments'] = []
                payload['attachments'].append(
                    {'name': filename,
                     'data': base64.b64encode(fdata).decode(),
                     'content-type': mimetypes.guess_type(filename)}
                )
        if 'on_behalf' in kwargs and kwargs['on_behalf'] is not None:
            payload['on_behalf'] = kwargs['on_behalf']
        return requests.post('{}/message'.format(self._base_url), json=payload, headers=self._headers)

    def delete_message(self, id):
        payload = {"id": id}
        res = requests.delete('{}/message'.format(self._base_url), json=payload, headers=self._headers)
        res.raise_for_status()
        return res


    def get_user(self, user_id, id_type='id', admin=False):
        params = {id_type: user_id}
        if admin:
            params['admin'] = True
        res = requests.get(
            self._base_url+'/user', params=params,
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    def who_am_i(self):
        params = {'session': True }
        res = requests.get(
            self._base_url+'/user', params=params,
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    def get_connections(self):
        res = requests.get(
            self._base_url+'/connection',
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    def add_connection(self, user, accept=None):
        data = {"user": user}
        if accept:
            data['accept'] = "true"
        elif not accept:
            data['accept'] = "false"

        res = requests.post(
            self._base_url+'/connection',
            headers=self._headers,
            json=data,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    def get_room_details(self, room_id, id_type='id', limit=1):
        params = { id_type: room_id, 'limit': limit }
        res = requests.get(
            '{}/room'.format(self._base_url),
            params=params,
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    def create_room(self, room_name):
        res = requests.post(
            '{}/room'.format(self._base_url),
            json={"name": room_name},
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    '''Display all members of a room'''
    def get_room_members(self, room_name, **kwargs):
        params = {}
        if 'on_behalf' in kwargs and kwargs['on_behalf'] is not None:
            params['on_behalf'] = kwargs['on_behalf']

        res = requests.get(
            '{}/room/{}/member'.format(self._base_url, room_name),
            headers=self._headers,
            params=params,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    '''Add a member or list of members to a room'''
    def add_room_members(self, room_name, member_email, **kwargs):
        users = []
        if not isinstance(member_email, list):
            users.append({"email": member_email})
        else:
            for user in member_email:
                users.append({"email": user})

        data = {"users": users}
        if 'on_behalf' in kwargs and kwargs['on_behalf'] is not None:
            data['on_behalf'] = kwargs['on_behalf']

        res = requests.post(
            '{}/room/{}/member'.format(self._base_url, room_name),
            json=data,
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    '''Remove a member or list of members from a room'''
    def remove_room_members(self, room_name, member_email, **kwargs):
        users = []
        if not isinstance(member_email, list):
            users.append({"email": member_email})
        else:
            for user in member_email:
                users.append({"email": user})

        data = {"users": users}
        if 'on_behalf' in kwargs and kwargs['on_behalf'] is not None:
            data['on_behalf'] = kwargs['on_behalf']

        res = requests.delete(
            '{}/room/{}/member'.format(self._base_url, room_name),
            json=data,
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res)

    def download_file(self, url, local_filename=None):
        if not local_filename:
            local_filename = url.split('/')[-1]
        r = requests.get(url, headers=self._headers, stream=True)
        r.raise_for_status()
        body = r.json()
        logging.debug('File: {}'.format(str(body)))
        with open(local_filename, 'wb') as f:
            bfile = io.BytesIO(base64.b64decode(body['message']))
            shutil.copyfileobj(bfile, f)
        return local_filename

    #    def send_stream_as_attachment(self, channel, attach, stream, disableEncoding=True, passthrough=True):

    @staticmethod
    def set_text(msg, text, data=None):
        if isinstance(text, SymphonyMessageML):
            msg['raw'] = {'message': text.__str__()}
        elif text.startswith('<messageML>') or text.startswith('<div '):
            msg['raw'] = {'message': text}
        else:
            msg['raw'] = {}
            msg['text'] = text
        if data is not None:
            msg['raw']['data'] = data
        return msg

    @staticmethod
    def read_cert(filename):
        return AriaService.base64_encode_file(filename)

    @staticmethod
    def base64_encode_file(filename):
        if not pathlib.Path(filename).exists():
            raise AriaError('File {} does not exist'.format(filename), None)
        with open(filename,'rb') as f:
            return base64.b64encode(f.read())


class AriaError(Exception):
    def __init__(self, text, res):
        self.text = text
        self.response = res


class SymphonyMessageML:
    def __init__(self):
        self._root = etree.Element('messageML')

    def root(self):
        return self._root

    @staticmethod
    def bold(text=None):
        _elem = etree.Element('b')
        if text is not None:
            _elem.text = text
        return _elem\

    @staticmethod
    def tbreak(text=None):
        _elem = etree.Element('br')
        if text is not None:
            _elem.text = text
        return _elem

    @staticmethod
    def hrule(text=None):
        _elem = etree.Element('hr')
        if text is not None:
            _elem.text = text
        return _elem\

    @staticmethod
    def italic(text=None):
        _elem = etree.Element('i')
        if text is not None:
            _elem.text = text
        return _elem

    def __str__(self):
        return etree.tostring(self._root).decode('utf-8')


__all__ = ['AriaService', 'SymphonyMessageML', 'AriaError']
