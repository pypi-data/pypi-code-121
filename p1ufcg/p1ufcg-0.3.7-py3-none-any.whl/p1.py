from builtins import str

import sys
import os
import io
import json
import pkg_resources
import logging

import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from questionary import Style

from .jsonfile import JsonFile, CorruptedJsonFile
from .colors import *
from .utils import cprint, _assert, is_posix_filename, data2json

P1STYLE=Style([
    ("highlighted","bold fg:#ffff00"),
    ("text","fg:#ccffcc"),
])

CONFIGDIR = os.path.expanduser('~/.p1/')
LOG_FILE = os.path.expanduser('~/.p1/logs.txt')
CONFIGFILE = CONFIGDIR + 'config.yaml'
SITES = [{"name": "prog1", "url": "http://p1ufcg.github.io"}]

def coverit():
    return 1

def get_config():
    if not os.path.exists(CONFIGFILE):
        if not os.path.isdir(CONFIGDIR):
            os.mkdir(CONFIGDIR)

        with io.open(CONFIGFILE, encoding="utf-8", mode="w") as config_file:
            config_file.write(
                "run:\n"
                "  py: python3\n"
                "  py2: python2\n\n"
            )

    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s (%(levelname)s@%(name)s) %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    # Uncomment to reduce too much data in logs
    #logging.getLogger("requests").setLevel(logging.WARNING)
    #logging.getLogger("cachecontrol.controller").setLevel(logging.WARNING)
    #logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    return JsonFile(CONFIGFILE)


def dirtype(path=""):
    path = os.path.abspath(os.path.expanduser(path))

    # p1 internal types of directories
    if path == os.path.expanduser('~/.p1'):
        return "config"

    elif os.path.basename(path) == '.p1':
        return "internal"

    # user content
    elif os.path.exists(path + '/.p1/assignment.json'):
        return "assignment"

    elif os.path.exists(path + '/.p1/activity.json'):
        return "activity"

    elif os.path.exists(path + '/.p1/collection.json'):
        return "collection"

    # corrupted/incomplete content
    elif os.path.isdir(path + '/.p1') and not path == os.path.expanduser('~'):
        return "corrupted"

    # directory contains a file with p1 tests
    elif os.path.exists(path + '/p1.json') or os.path.exists(path + '/p1.yaml'):
        return "p1-able"

    # not a p1 directory
    return None


def validate_p1_object(json):
    def is_valid_mode(mode):
        # 2to3: isinstance(mode, basestring) and\
        return mode is None or\
               isinstance(mode, str) and\
               len(mode) <= 3 and\
               all(d in 'rwxo' for d in mode.lower())

    assert 'files' in json, "missing files property"
    assert type(json) is dict, "json is not an object"

    files = json['files']
    assert all('content' in f for f in files), "missing content in file(s)"
    assert all('name' in f for f in files), "missing name in file(s)"
    assert all(is_posix_filename(f['name'], "/") for f in files), "non posix portable file(s) name(s)"
    assert all(is_valid_mode(f.get('mode')) for f in files), "invalid mode in file(s)"
    if not (len(files) == len(set([f['name'] for f in files]))):
        filenames = [f['name'] for f in files]
        repeated = list(set([fn for fn in filenames if filenames.count(fn) > 1]))
        msg = f"file repeated: {' '.join(repeated)}"
        logging.warning(msg)


def parse_file_spec(fspec):

    # normalize fspec
    while fspec.count(',') < 2:
        fspec = fspec + ','

    # separate filename and details
    data = fspec.split(",")
    filename = data[0].strip()
    details = [e.strip() for e in data[1:]]

    # consume public or private specification
    if 'public' in details:
        details.remove('public')

    elif 'private' in details:
        details.remove('private')

    else:
        details.remove('')

    # check mode
    mode = details[0]

    return filename, mode


def is_single_line_string(text):
    return '\n' not in text and '\r' not in text


class Site:
    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url
        self._session = None
        self._googappuid = None
        for s in SITES:
            if s['name'] == name:
                self.url = s['url']


    def api_url(self):
        urls = self.urls()
        assert urls, "no urls provided by site"
        url = self.api_full_url(urls.get('api-url'))
        if url.startswith("http://https"):
            url = url[7:]
        return url


    def api_login_url(self):
        urls = self.urls()
        if urls is None:
            return None

        return self.api_full_url(urls.get('login-url'))


    def api_access_url(self):
        urls = self.urls()
        if urls is None:
            return None

        return self.api_full_url(urls.get('access-url'))


    def api_full_url(self, url):
        if url is None:
            return None

        if url.startswith('http://') or url.startswith('https://'):
            return url

        if url.startswith('/'):
            return f"{self.urls()['api-url']}{url}"

        return f"{self.urls['api-url']}/{url}"


    def login_url(self):
        urls = self.urls()
        if urls is None:
            return None

        return self.full_url(urls.get('login'))


    def token_url(self):
        urls = self.urls()
        if urls is None:
            return None

        return self.full_url(urls['token'])


    def full_url(self, url):
        if url is None:
            return None

        if url.startswith('http://') or url.startswith('https://'):
            return url

        if url.startswith('/'):
            return self.url + url

        return self.url + '/' + url


    def urls(self):
        s = self.get_session()
        try:
            response = s.get(self.url + '/tst.json', allow_redirects=True)
        except requests.ConnectionError:
            _assert(False, "Connection failed... check your internet connection")

        if not response.ok:
            return None

        response.encoding = 'utf-8'
        try:
            resource = response.json()
            resource['_response'] = response

        except ValueError:
            return None

        return resource


    def save_cookies(self, response):
        cookies_file = JsonFile(os.path.expanduser('~/.p1/cookies.json'))
        cookies_file.writable = True
        new_googappuid = response.cookies['GOOGAPPUID'] if response.cookies else None
        if not new_googappuid:
            logging.warning("no GOOGAPPUID cookie in server response (setting value to 0)")
            new_googappuid = '0'

        if not new_googappuid.isdigit() or not (0 <= int(new_googappuid) < 1000):
            logging.warning("invalid value for GOOGAPPUID cookie: %s (setting value to 0)" % new_googappuid)
            new_googappuid = '0'

        if new_googappuid != self._googappuid:
            logging.info("saving new GOOGAPPUID cookie: %s" % new_googappuid)
            cookies_file[self.name] = {"GOOGAPPUID": new_googappuid}
            cookies_file.save()

    def get(self, path):
        s = self.get_session()
        url = "%s%s" % (self.api_url(), path) if path.startswith('/') else path
        try:
            response = s.get(url, allow_redirects=True)
            logging.info('GET %s (%s)' % (url, response.status_code))
        except requests.ConnectionError:
            _assert(False, "Connection failed... check your internet connection")

        if not response.ok:
            self.last_response = response
            return response

        self.save_cookies(response)
        response.encoding = 'utf-8'
        return response

    def get_activity(self, key):
        s = self.get_session()
        url = "%s/%s" % (self.api_url(), key)
        try:
            response = s.get(url, allow_redirects=True)
            logging.info('GET %s (%s)' % (url, response.status_code))
        except requests.ConnectionError:
            _assert(False, "Connection failed... check your internet connection")

        if not response.ok:
            self.last_response = response
            return (None, response)

        self.save_cookies(response)
        response.encoding = 'utf-8'
        try:
            resource = response.json()
            resource['_response'] = response
            validate_p1_object(resource)

        except ValueError:
            #_assert(False, "Resource is not valid json")
            logging.warning('ValueError during resource processing (in get_activity())')
            return (None, response)

        except AssertionError as e:
            _assert(False, "Invalid activity: %s" % str(e))

        return (resource, response)

    def get_directory(self, key):
        s = self.get_session()
        api_url = self.api_url()
        url = "%s/%s/p1.yaml" % (api_url, key)
        try:
            response = s.get(url, allow_redirects=True)
            logging.info('GET %s (%s)' % (url, response.status_code))
        except requests.ConnectionError:
            _assert(False, "Connection failed... check your internet connection (1)")

        # process response
        if not response.ok:
            self.last_response = response
            return (None, response)

        response.encoding = 'utf-8'
        try:
            import yaml
            resource = yaml.load(response.text, Loader=yaml.FullLoader)
            resource['_response'] = response

        except Exception as e:
            cprint(YELLOW, "Atividade mal formada: %s" % url)
            logging.info('Falied parsing activity yaml' % (url, response.status_code))
            raise e

        # gather files
        files = resource.get('files') or []
        files.append({
            "name": "p1.yaml",
            "content": response.text,
            "mode": "ro"
        })

        ## add text file if required
        if 'text' in resource and is_single_line_string(resource['text']):
            files.append({
                "name": resource['text'],
                "content": '%s/%s/%s' % (api_url, key, resource['text']),
                "mode": "ro"
            })

        ## add included files
        files_filenames = [f['name'] for f in files]
        for fspec in resource['include']:
            filename, mode = parse_file_spec(fspec)
            if filename not in files_filenames:
                files.append({
                    'name': filename,
                    'content': '%s/%s/%s' % (api_url, key, filename),
                    'mode': mode
                })
            else:
                entry = next(e for e in files if e['name'] == filename)
                entry['mode'] = mode

        ## fetch missing files
        for f in files:
            if f['content'].startswith('http://') or f['content'].startswith('https://'):
                url = '%s/%s/%s' % (api_url, key, f['name'])
                try:
                    response = s.get(url)
                    logging.info('GET %s (%s)' % (url, response.status_code))
                except requests.ConnectionError:
                    _assert(False, "Connection failed... check your internet connection")

                _assert(response.ok, "%s\nFile request failed: %s (%d)" % (url, response.reason, response.status_code))
                response.encoding = 'utf-8'
                f['content'] = response.text

        return ({
            'files': files,
        }, response)


    def get_session(self, headers=None, cookies=None):
        """
        Return a pre-configured requests session object, containing
        the proper headers, cookies and cache control decorator.
        """
        # is there a previous session?
        if self._session:
            return self._session

        # create basic session objet
        s = requests.session()

        # add headers
        s.headers = headers or { 'X-P1-Version': pkg_resources.get_distribution('p1ufcg').version }
        token = JsonFile(os.path.expanduser('~/.p1/tokens.json')).get(self.name)
        if token:
            s.headers['Authorization'] = 'Bearer %s' % token

        # set cookies
        allcookies = JsonFile(os.path.expanduser('~/.p1/cookies.json'))
        cookies = cookies or allcookies.get(self.name) or {}
        if cookies:
            self._googappuid = cookies['GOOGAPPUID']
            logging.info("setting up session with GOOGAPPUID cookie: %s" % self._googappuid)
        else:
            logging.warning("setting up session WITHOUT GOOGAPPUID")
        s.cookies.update(cookies)

        self._session = CacheControl(s, cache=FileCache(os.path.expanduser('~/.p1/cache')))
        return self._session

    def send_answer(self, answer, key):
        s = self.get_session()
        url = "%s/%s/answers" % (self.api_url(), key)
        data = data2json(answer).encode('utf-8')
        try:
            response = s.post(url, data=data, allow_redirects=True)
        except requests.ConnectionError:
            _assert(False, "Connection failed... check your internet connection (1)")

        return response

    def post(self, target, data, headers=None, cookies=None):
        # BEWARE: this is an attempt to make a simple facility method
        #         configures and performs an HTTP POST request to
        #         the given site.
        #
        # target: is either a target within the site or the full url
        s = self.get_session(headers=headers, cookies=cookies)
        url = "%s%s" % (self.url, target) if target.startswith('/') else target
        response = s.post(url, data=data2json(data), allow_redirects=True)
        logging.info('POST %s (%s)' % (url, response.status_code))
        self.save_cookies(response)
        return response


def get_site(name=None, url=None):
    assert name is None or url is None

    if url:
        return Site(url=url)

    elif name == "_DEFAULT":
        index = 0

    else:
        index = next((i for i in range(len(SITES)) if SITES[i]['name'] == name), None)
        if index is None:
            return None

    return Site(name=SITES[index]['name'])
    #return Site(name=get_config()['sites'][index]['name'])
