#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import os
import signal
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
import urllib

if PY2:
    import urllib2 as urllib2
    from urlparse import urlparse

    reload(sys)
    sys.setdefaultencoding('utf-8')

if PY3:
    import urllib.request as urllib2
    from urllib.parse import urlparse

    urllib.urlencode = urllib.parse.urlencode

import subprocess
import time
import datetime
import re
import logging
import hashlib
import base64

import tempfile
import threading
import getopt
from logging.handlers import RotatingFileHandler
import json
import random
import platform
import socket

import uuid
import inspect
import getpass

PLATFORM = platform.system().lower()
PYTHON_PATH = '/usr/bin/python'


def init_log():
    dirs = ['/tmp/', '/var/', '/etc/', '/bin/', '/var/log/']
    for d in dirs:
        if not os.path.exists(d):
            os.mkdir(d)
    user = getpass.getuser()
    client_log_filename = '/var/log/cli.log'
    try:
        if PLATFORM != 'windows':
            _p = os.popen('which python').read().strip()
            if _p != '' and len(_p) > 0:
                PYTHON_PATH = _p
    except Exception as er:
        pass

    log_dir = os.path.dirname(client_log_filename)
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    # if user=='root':
    #     os.chmod(log_dir,0666)
    log_fmt_str = '%(asctime)-25s %(module)s:%(lineno)d  %(levelname)-8s %(message)s'
    if PY2:
        logging.basicConfig(level=logging.DEBUG,
                            format=log_fmt_str,
                            filemode='a+', filename=client_log_filename)
    if PY3:
        log_fmt_str = '%(asctime)s %(module)s:%(lineno)d  %(levelname)s %(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=log_fmt_str, filename=client_log_filename)
    logger = logging.getLogger('CLI')
    file_handler = RotatingFileHandler(filename=client_log_filename, maxBytes=100 * 1024 * 1024, backupCount=3)
    formatter = logging.Formatter(log_fmt_str)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if user == 'root' and PLATFORM != 'windows':
        try:
            if len(os.popen('command -v chattr').read()) > 1:
                os.popen('chattr -a %s' % (client_log_filename)).read()
                os.chmod(client_log_filename, 766)
                # os.popen('chattr +a %s'%(client_log_filename)).read()
        except Exception as er:
            pass
    try:
        os.chmod(client_log_filename, 766)
    except Exception as er:
        pass
    return logger


logger = logging.getLogger('CLI')
log = logger
IS_INIT_GLOBAL_LOG = False
HELP_DOC = '''

'''


class ZbxCommon(object):
    def __init__(self, server_url=''):
        self.machine_id = ''
        self.server = server_url
        self.config = {}
        self.args = {}
        self.log = logger
        self.obj_token = ''
        self.auth_uuid = ''
        self.token = ''
        if len(sys.argv) == 2 and len(sys.argv[1]) == 36:
            self.get_param('')

    def init_log(self):
        global logger, IS_INIT_GLOBAL_LOG
        if not IS_INIT_GLOBAL_LOG:
            IS_INIT_GLOBAL_LOG = True
            logging = init_log()

    def urlencode(self, str):
        reprStr = repr(str).replace(r'\x', '%')
        return reprStr[1:-1]

    def set_obj_token(self, token):
        self.obj_token = token

    def set_token(self, token):
        self.token = token

    def get_machine_id(self):
        return self.get_product_uuid()

    def id(self):
        return self.get_product_uuid()

    def get_product_uuid(self):
        if self.machine_id != '' and len(self.machine_id) == 36:
            return self.machine_id
        product_uuid = ''
        # if os.path.isfile('/sys/devices/virtual/dmi/id/product_uuid'):
        #     product_uuid=self.execute('cat /sys/devices/virtual/dmi/id/product_uuid').strip()
        if product_uuid == "":
            uuid_file = '/etc/machine_id'
            if not os.path.exists(uuid_file):
                product_uuid = self.get_uuid()
                with open(uuid_file, 'w') as file:
                    file.write(product_uuid)
            else:
                with open(uuid_file, 'r') as file:
                    product_uuid = file.read()
        self.machine_id = product_uuid.strip()
        return product_uuid.strip()

    def get_basic_auth(self, user='', pwd=''):
        s = user.strip() + ':' + pwd.strip()
        if PY2:
            return 'Basic ' + base64.encodestring(s).strip()
        if PY3:
            return 'Basic ' + str(base64.encodestring(s.encode('utf-8')), 'utf-8').strip()

    def download(self, filename, directory, filepath=''):
        try:
            if filepath == '':
                filepath = filename
            data = {'file': filename, 'dir': directory}
            data = urllib.urlencode(data)
            if filename.startswith('http://') or filename.startswith('https://'):
                http_url = filename
                if http_url.endswith('/'):
                    http_url = http_url[0:len(http_url) - 1]
                if http_url.rindex('/') > 0 and http_url.rindex('/') < len(http_url):
                    filename = http_url[http_url.rindex('/') + 1:]
                filename = filename.replace('?', '')
                filepath = filename
            else:
                # http_url = '%s/%s/download?%s' % (server_url, default_module, data)
                http_url = self.get_server_uri('download?%s' % (data))

            def _download(url, data, filepath):
                # logger.info('download file url:%s'%(str(url)))
                request = urllib2.Request(url)
                request.add_header('User-Agent', 'CLI(1.0)')
                if filename.startswith('http://') or filename.startswith('https://'):
                    request.add_header('auth-uuid', self._get_config('auth-uuid'))
                conn = urllib2.urlopen(request)
                f = open(filepath, 'wb')
                f.write(conn.read())
                f.close()

            _download(http_url, data, filepath)
            try:
                line = ''
                with open(filepath, 'r') as _file:
                    if PY3:
                        try:
                            _file.readline().encode()
                        except Exception as er:
                            pass
                    else:
                        line = str(_file.readline()).strip()
                if line.startswith('redirect:http://') or line.startswith('redirect:https://'):
                    _download(line, data, filepath)
            except Exception as er:
                print('(error) %s' % (str(er)))
                logger.error(er)
        except Exception as e:
            logger.error(e)
            print('(error) %s' % (str(e)))

    def upload(self, filepath, directory):
        return self._upload(self.get_server_uri('upload'), filepath, directory)

    def login(self, user='', password=''):
        url = self.get_server_uri('login')
        ret = self.url_fetch(url, {'param': json.dumps({'u': user, 'p': password})})
        if len(ret) == 36:
            self._set_config('auth-uuid', str(ret).strip())
            self.auth_uuid = str(ret).strip()
            return True
        else:
            return False

    def _upload(self, url, filepath, directory):
        boundary = '----------%s' % hex(int(time.time() * 1000))
        data = []
        data.append('--%s' % boundary)
        fr = open(filepath, 'rb')
        filename = os.path.basename(filepath)
        data.append('Content-Disposition: form-data; name="%s"\r\n' % 'filename')
        data.append(filename)
        data.append('--%s' % boundary)
        data.append('Content-Disposition: form-data; name="%s"\r\n' % 'dir')
        data.append(directory)
        data.append('--%s' % boundary)
        data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % ('file', filename))
        data.append('Content-Type: %s\r\n' % 'image/png')

        if PY3:
            http_body = "\r\n".join(data) + '\r\n'
            from io import BytesIO
            f = BytesIO()
            f.write(http_body.encode(encoding="utf-8"))
            f.write(fr.read())
            f.write(('\r\n--%s--\r\n' % boundary).encode(encoding="utf-8"))
        else:
            data.append(fr.read())
            data.append('--%s--\r\n' % boundary)
            http_body = '\r\n'.join(data)
        fr.close()

        try:
            if PY3:
                req = urllib2.Request(url, data=f.getvalue())
            else:
                req = urllib2.Request(url, data=http_body)
            req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
            req.add_header('User-Agent', 'Mozilla/5.0')
            req.add_header('Referer', 'http://remotserver.com/')
            req.add_header('auth-uuid', self.auth_uuid)
            resp = urllib2.urlopen(req, timeout=50)
            qrcont = resp.read()
            return True
        except Exception as e:
            logger.error(e)
            print('(error)%s' % (str(e)))
            return False

    def url_fetch_witherr(self, url, data=None, header={}, timeout=30, httpCmd=''):
        return self._url_fetch(url, data=data, header=header, timeout=timeout, httpCmd=httpCmd)

    def get(self, url, timeout=30, return_json=True):
        data = self._url_fetch(url, timeout=timeout)
        try:
            if return_json:
                return json.loads(data)
            else:
                return data
        except Exception as er:
            return data

    def _exec(self, cmd, timeout=10):
        result = {'result': ''}

        def run(cmd, result):
            pipe = os.popen(cmd)
            try:
                result['result'] = pipe.read()
                pipe.close()
            except Exception as er:
                pass
            finally:
                try:
                    pipe.close()
                except Exception as er:
                    pass

        t = threading.Thread(target=run, args=(cmd, result,))
        t.start()
        t.join(timeout=timeout)
        return result['result']

    def get_server_uri(self, action=''):
        if 'CLI_SERVER' in os.environ and os.environ['CLI_SERVER'] != '':
            self.server = os.environ['CLI_SERVER']
            return self.server + '/cli/%s' % (action)
        if self.server == '':
            # info=self.execute('cli info',3)
            info = json.loads(self._exec('cli info'))
            if 'server' in info.keys():
                self.server = info['server']
        return self.server + '/cli/%s' % (action)

    def jf(self, data, where='1=1', columns='*', order='', limit='0,10000000'):
        def _query(data, _sql):
            con = None
            cols = set()
            keyword = ['ALTER',
                       'CLOSE',
                       'COMMIT',
                       'CREATE',
                       'DECLARE',
                       'DELETE',
                       'DENY',
                       'DESCRIBE',
                       'DOMAIN',
                       'DROP',
                       'EXECUTE',
                       'EXPLAN',
                       'FETCH',
                       'GRANT',
                       'INDEX',
                       'INSERT',
                       'OPEN',
                       'PREPARE',
                       'PROCEDURE',
                       'REVOKE',
                       'ROLLBACK',
                       'SCHEMA',
                       'SELECT',
                       'SET',
                       'SQL',
                       'TABLE',
                       'TRANSACTION',
                       'TRIGGER',
                       'UPDATE',
                       'VIEW',
                       'GROUP', ]
            for row in data:
                for k in list(row.keys()):
                    k2 = k
                    if str(k).upper() in keyword:
                        # k2='_'+str(k)
                        k2 = '`_%s`' % (k)
                        row[k2] = row[k]
                    else:
                        k2 = '`%s`' % (k)
                        row[k2] = row[k]
                    del row[k]
                    cols.add(k2)

            try:
                import sqlite3

                try:
                    con = sqlite3.connect(':memory:')
                except Exception as er:
                    print(er)

                if len(data) > 0:
                    sql = 'create table data(%s)' % ','.join(cols)
                    try:
                        con.execute(sql)
                    except Exception as er:
                        logger.error(er)

                for row in data:
                    keys = []
                    vals = []
                    foo = []

                    for k, v in row.items():
                        keys.append(k)
                        # vals.append("'%s'" % (str(v).replace("'", "\\'")))
                        vals.append(v)
                        foo.append("?")
                    sql = 'insert into data(%s) values(%s)' % (','.join(keys), ','.join(foo))
                    con.execute(sql, tuple(vals))
                    con.commit()
                cur = con.execute(_sql)

                rows = []
                fields = []
                for f in range(len(cur.description)):
                    if isinstance(cur.description[f][0], str):
                        fields.append(cur.description[f][0])
                for _row in cur:
                    j = 0
                    row = {}
                    for i in _row:
                        row[fields[j]] = i
                        j = j + 1
                    rows.append(row)
                return rows
            except Exception as er:
                logger.error(er)
            finally:
                try:
                    con.close()
                except Exception as er:
                    pass

        if order != '':
            order = 'order by %s' % (order)
        sql = "select %s from data where 1=1 and %s %s limit %s" % (columns, where, order, limit)
        return _query(data, sql)

    def __getattr__(self, item):

        def _cli(param=None, *args, **kwargs):
            if param == None:
                param = {'i': self.ip()}
            if isinstance(param, dict) and 'i' not in param.keys():
                param['i'] = self.ip()
            for k, v in param.items():
                if isinstance(v, dict) or isinstance(v, list):
                    param[k] = json.dumps(v)
            params = {'param': json.dumps(param)}
            url = self.get_server_uri(str(item))
            ret = ''
            try:
                ret = self._url_fetch(url, params)
            except Exception as er:
                logger.error(url, params)
            try:
                return json.loads(ret)
            except Exception as er:
                return ret

        return _cli

    def post(self, url, data=None, header={}, timeout=30, return_json=True):
        data = self._url_fetch(url, data=data, header=header, timeout=timeout)
        try:
            if return_json:
                return json.loads(data)
            else:
                return data
        except Exception as er:
            return data

    def url_fetch(self, url, data=None, header={}, timeout=30, httpCmd='', debug=False):
        try:
            return self._url_fetch(url, data=data, header=header, timeout=timeout, httpCmd=httpCmd, debug=debug)
        except Exception as er:
            # logger.error('url_fetch error:%s'+str(er))
            print(er)
            return ''

    def _get_config(self, key):
        home = os.path.expanduser('~')
        fn = home + '/.cli'
        content = ''
        data = {}
        try:
            if os.path.isfile(fn):
                with open(fn) as f:
                    content = f.read()
                    content = str(content).strip()
                lines = re.split(r'\n', content)
                for line in lines:
                    line = line.strip()
                    pos = line.find('=')
                    if pos > 0:
                        data[line[0:pos]] = line[pos + 1:]
                if len(data) > 0:
                    self.config = data
        except Exception as er:
            logger.error(er)
        if key in self.config.keys():
            return self.config[key]
        else:
            return ''

    def _set_config(self, key, value):
        home = os.path.expanduser('~')
        fn = home + '/.cli'
        kv = []
        ks = ['token', 'auth-uuid']
        for _k in ks:
            if not _k in self.config.keys():
                self.config[_k] = ''
        self.config[key] = value
        for k, v in self.config.items():
            kv.append('%s=%s' % (k, v))
        try:
            if os.path.isfile(fn):
                with open(fn, 'w') as f:
                    f.write("\n".join(kv))
                return True
            else:
                try:
                    with open(fn, 'w') as f:
                        f.write("\n".join(kv))
                except Exception as e:
                    logger.error(e)
        except Exception as er:
            logger.error(er)
            return False

    def _url_fetch(self, url, data=None, header={}, timeout=30, httpCmd='', debug=False):
        html = ''
        handle = None
        machine_id = self.get_product_uuid()
        key = self._get_config('auth-uuid')
        if self.auth_uuid != '':
            key = self.auth_uuid
        token = self._get_config('token')
        if self.token != '':
            token = self.token
        try:
            headers = {
                'User-Agent': 'CLI agent(1.0)',
                'auth-uuid': key,
                'token': token,
                'machine-id': machine_id,
            }
            if len(header) > 0:
                for k, v in header.items():
                    headers[k] = v
                if self.token != '':
                    headers['token'] = self.token
                if self.obj_token != '':
                    headers['obj-token'] = self.obj_token
            if data != None:
                data = urllib.urlencode(data)
                if PY3:
                    data = data.encode('utf-8', 'ignore')
                # print(data)

            req = urllib2.Request(
                url=url,
                headers=headers,
                data=data
            )
            if httpCmd != "":
                req.get_method = lambda: httpCmd

            handle = urllib2.urlopen(req, timeout=timeout)

            html = handle.read()
            cm = r'<meta[^>]*charset=[\'\"]*?([a-z0-8\-]+)[\'\"]?[^>]*?>'
            if PY3:
                cm = cm.encode('utf-8', 'ignore')
            charset = re.compile(cm, re.IGNORECASE).findall(html)
            if len(charset) > 0:
                if charset[0] == 'gb2312':
                    charset[0] = 'gbk'
                if PY2:
                    html = unicode(html, charset[0])
            if PY3:
                return html.decode('utf-8', 'ignore')
        except Exception as e:
            logger.error(e)
            raise Exception(e)
        finally:
            if handle != None and handle.fp != None:
                try:
                    handle.fp.close()
                except Exception as er:
                    pass

        return html

    def _cmdline_args(self, s):
        import re
        s = re.subn(r'\\"', '{,,}', s)[0]
        s = re.subn(r"\\'", '{,}', s)[0]
        l = re.findall(r"'[^']+?'|\"[^\"]*?\"", s, re.IGNORECASE | re.MULTILINE)
        # l= re.findall(r"'[\s\S]*[\']?'|\"[\s\S]*[\"]?\"",s,re.IGNORECASE|re.MULTILINE)
        for i, v in enumerate(l):
            s = s.replace(v, '{' + str(i) + '}')
        p = re.split(r'\s+', s)
        ret = []

        def repl(a):
            i = re.findall(r'\{\d+\}', a.group(0))
            a = re.sub('\{\d+\}', l[int(re.sub(r'^{|}$', '', i[0]))], a.group(0))
            return a

        for a in p:
            # print a
            i = re.findall(r'\{\d+\}', a)
            if len(i) > 0:
                a = re.sub(r'[\s\S]+', repl, a)
            if re.match(r"'[\s\S]+'", a) or re.match(r'"[\s\S]+"', a):
                a = re.sub("^'|'$|^\"|\"$", '', a)
            a = re.subn(r"\{\,\,\}", '\"', a)[0]
            a = re.subn(r"\{\,\}", "\'", a)[0]
            ret.append(a)
        return ret

    def getopt(self, inputs):
        if isinstance(inputs, basestring):
            inputs = self._cmdline_args(inputs)

        def ptype(input):
            if input == "":
                return (0, "")
            if "-" == input[0] and len(input) == 2:
                return (1, input[1])
            if "--" == input[:2] and len(input) >= 4:
                return (2, input[2:])
            return (0, "")

        def istype(input):
            if len(input) <= 0:
                return 0
            if "-" == input[0]:
                return 1
            return 0

        ret = {}
        u = 0
        ucount = len(inputs)
        icount = 0
        ls = []
        if ucount >= 1:
            while 1:
                if u >= ucount:
                    break
                if istype(inputs[u]) == 1:
                    break

                ls.append(inputs[u])
                u += 1

            inputs = inputs[u:]
            icount = len(inputs)

        if icount >= 1:
            i = 0
            state = 0
            while 1:
                t, name = ptype(inputs[i])
                for c in range(1):
                    if t == 0:
                        i += 1
                        break
                    if i + 1 < icount:
                        tt, tname = ptype(inputs[i + 1])
                        if tt != 0:
                            ret[name] = ""
                            i += 1
                            break
                        ret[name] = inputs[i + 1]
                        i += 2
                        break
                    ret[name] = ""
                    i += 1
                    break
                if i >= icount:
                    break
        return (ret)

    def parse_argv(self, argv):
        data = {}
        long_args = []
        short_args = []
        for v in argv:
            if v.startswith('--'):
                long_args.append(v.replace('--', '') + "=")
            elif v.startswith('-'):
                short_args.append(v.replace('-', ''))
        opts = getopt.getopt(argv, ":".join(short_args) + ":", long_args)
        for opt in opts[0]:
            data[opt[0].replace('-', '')] = opt[1]
        if len(data) > 0:
            return data
        else:
            return argv

    def md5(self, src):
        m2 = hashlib.md5()
        if PY3:
            src = str(src).encode('utf-8', 'ignore')
        m2.update(src)
        return m2.hexdigest()

    def now_datetime(self):
        now_datetime = time.strftime('_%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
        return now_datetime

    def _date_format(self, fmt):
        return time.strftime(fmt, time.localtime(time.time()))

    def date(self, fmt='%Y-%m-%d'):
        return self._date_format(fmt)

    def time(self, fmt='%H:%M:%S'):
        return self._date_format(fmt)

    def now(self, fmt='%Y-%m-%d %H:%M:%S'):
        return self._date_format(fmt)

    def match(self, s, m, o='ima'):
        flags = 0
        is_all = False
        for i in range(0, len(o)):
            if o[i] == 'i':
                flags = flags | re.IGNORECASE
            if o[i] == 'm':
                flags = flags | re.MULTILINE
            if o[i] == 'a':
                is_all = True
        r = re.compile(m, flags=flags)
        ret = r.findall(s)
        if is_all:
            return json.dumps(ret)
        if len(ret) > 0:
            return ret[0]
        else:
            return ''

    def write_tempfile(self, content):
        name = self.uuid()
        path = tempfile.gettempdir() + os.path.sep + name
        with open(path, 'wb') as fp:
            fp.write(content)
        return path

    def execute_shell(self, cmd, timeout=30, url='', debug=False):
        try:
            path = self.write_tempfile(cmd)
            os.chmod(path, 777)
        except Exception as er:
            logger.error(er)
            return str(er)
        try:
            lines = str(cmd).split("\n")
            if len(lines) > 0 and lines[0].find('bash') != -1 and debug:
                content = ZbxCommand("/bin/bash -x '%s'" % (path)).run(timeout=timeout, url=url)
            else:
                content = ZbxCommand(path).run(timeout=timeout, url=url)
            try:
                return json.loads(content)
            except Exception as er:
                return content
        except Exception as err:
            logger.error(err)
            return ""
        finally:
            try:
                os.unlink(path)
            except Exception as er:
                pass

    def execute(self, cmd, timeout=30, url=''):
        try:
            content = ZbxCommand(cmd).run(timeout=timeout, url=url)
            try:
                return json.loads(content)
            except Exception as er:
                return content
        except Exception as err:
            logger.error(err)
            return ""

    def get_param(self, key=''):
        if len(self.args) == 0 and len(sys.argv) == 2 and len(sys.argv[1]) == 36:
            self.args = self.params({'k': sys.argv[1]})
        if key == '':
            return self.args
        else:
            return self.args.get(key, '')

    def check_param(self, key='', force_exit=True):
        if key == '':
            key = str(sys.argv[1]).strip()
        if len(key) != 36 and force_exit:
            logger.warning('exit key %s' % (key))
            sys.exit(1)
        # params=self.execute('cli params -k %s'%(key))
        params = self.params({'k': key})
        if isinstance(params, dict):
            self.args = params
        if not isinstance(params, dict) and force_exit:
            logger.warning('params is not dict')
            sys.exit(1)
        if not 'ip' in params and force_exit:
            logger.warning('params not contains ip key')
            # sys.exit(1)
        for k, v in params.items():
            if str(v).strip() == '':
                logger.warning('params  key %s is null' % (str(k)))
                if force_exit:
                    sys.exit(1)
                else:
                    return False
        return True

    def get_one_ip(self):
        # ret = [x for x in self.get_all_ip_list() if x.startswith('10') or x.startswith('172') or x.startswith('192')]
        ret = [x for x in self.get_all_ip_list() if x.startswith('10.') or x.startswith('172.') or x.startswith('192.')]
        if len(ret) > 1:
            return ret[0]
        return ''.join(ret)

    def get_all_ip_list(self):
        if platform.system().lower() == 'windows':
            name, xx, ips = socket.gethostbyname_ex(socket.gethostname())
            return ips
        else:
            # cmdline = "ip a | egrep \"^\s*inet.*\" | grep -v inet6 | awk '{print $2}' | awk -v FS='/' '{print $1}'"
            cmdline = "ip a"
            ret = self.execute(cmdline)
            ips = re.findall(r'inet\s*(\d+\.\d+\.\d+\.\d+)', ret)
            if len(ips) == 0:
                return [self._get_host_ip()]
            else:
                return ips
            # lip=re.split(r'\n',ret)
            # ips=[]
            # for ip in lip:
            #     if str(ip).strip ()!='':
            #       ips.append(ip.strip())
            # return ips

    def render(self, tpl_str, *args, **kwargs):
        from jinja2 import Environment
        tpl = Environment().from_string(tpl_str)
        return tpl.render(*args, **kwargs)

    def get_mysql_connection(self, dsn_str):
        import dsnparse
        dsn = dsnparse.parse(dsn_str)
        import pymysql
        connection = pymysql.connect(host=dsn.host,
                                     user=dsn.user,
                                     port=dsn.port,
                                     password=dsn.password,
                                     database=dsn.database,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection


    def mysql_query(self, connection, sql, *args):
        with connection.cursor() as cursor:
            sql=str(sql).strip()
            if re.match(r'select|show',sql,re.IGNORECASE):
                cursor.execute(sql, args)
                rows = cursor.fetchall()
                return rows
            else:
                return cursor.execute(sql, args)

    def get_uuid(self):
        return str(uuid.uuid4())

    def uuid(self):
        return self.get_uuid()

    def jq(self, data, key, pretty=False):
        return self._get_json(data, key, pretty=False)

    def _get_json(self, data, key, output='text', sep=' ', quote='', pretty=False):
        def parse_dict(data, key):
            return data.get(key, None)

        def parse_list(data, key):
            ret = []
            if re.match(r'^\d+$', key):
                return data[int(key)]

            for i in range(0, len(data)):
                if isinstance(data[i], dict):
                    if key == '*':
                        for j in data[i].keys():
                            ret.append(data[i].get(j, None))
                    else:
                        ret.append(data[i].get(key, None))
                elif isinstance(data[i], list):
                    for j in range(0, len(data[i])):
                        if key == '*':
                            ret.append(data[i][j])
                        else:
                            ret.append(data[i][j].get(key, None))

            return ret

        if key.find(',') != -1:
            ks = key.split(',')
        else:
            ks = key.split('.')

        for k in ks:
            if isinstance(data, list):
                data = parse_list(data, k)
                # print(k,data)
            elif isinstance(data, dict):
                data = parse_dict(data, k)
                # print(k,data)
        return data

    def _get_host_ip(self):
        ip = '127.0.0.1'
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception as er:
            try:
                ip = self.get(self.get_server_uri('ip'))
                return str(ip).strip()
            except Exception as er:
                return self.get_one_ip()
        finally:
            try:
                if s != None:
                    s.close()
            except Exception as er:
                pass
        return ip

    def get_ip2mac_dict(self):
        cmdline = "ip a"
        ret = self.execute(cmdline)
        ips = re.findall(r'inet\s*(\d+\.\d+\.\d+\.\d+)[^\r\n]+[\r\n]\s*ether\s+([\w\:]+)\s', ret)
        data = {}
        for i in ips:
            data[i[0]] = i[1]
        return data

    def ip(self):
        return self._get_host_ip()

    def replace(self, s, o, n):
        ret = re.subn(re.compile(o, re.MULTILINE | re.IGNORECASE), n, s)
        if len(ret) > 0:
            return ret[0].strip()
        else:
            return s.strip()

    def join(self, s, sep=',', wrap='', trim_null=True):
        if isinstance(s, list):
            if trim_null:
                t = []
                for i in s:
                    if isinstance(i, str) or isinstance(i, unicode):
                        if i.strip() == '':
                            continue
                    if i == None:
                        continue
                    t.append(i)
                s = t
            if wrap != '':
                s = ['%s%s%s' % (wrap, str(i), wrap) for i in s]
            return sep.join(s)
        return s

    def splitj(self, s, line_pat="\n", field_pat="\s{1,}", header='', ftype='table'):
        s = s.strip()
        lines = re.split(line_pat, s)
        if len(lines) == 0:
            return []
        data = []
        if ftype == 'table':
            if header == '':
                header = lines[0]
            fields = re.split(field_pat, header)
            for i in lines[1:]:
                vals = re.split(field_pat, i)
                k = 0
                row = {}
                if len(vals) <= len(fields):
                    for j in vals:
                        row[fields[k]] = vals[k]
                        k = k + 1
                    data.append(row)
        elif ftype == 'kv':
            data = {}
            for i in lines:
                vals = re.split(field_pat, i)
                if len(vals) == 2:
                    data[vals[0]] = vals[1]
        return data

    def split(self, s, sep, trim_null=True):
        ret = re.split(re.compile(sep, re.MULTILINE | re.IGNORECASE), s)
        rets = []
        if trim_null:
            for i in ret:
                if str(i).strip() == '':
                    continue
                else:
                    rets.append(i)
        else:
            return ret
        return rets

    def rand(self):
        return random.random()

    def randint(self, min=1, max=100):
        return random.randint(min, max)

    def json_encode(self, obj):
        return json.dumps(obj)

    def json_decode(self, s):
        return json.loads(s)

    def format_shell_str(self, strs):
        return strs.replace('\\', '\\\\').replace('"', '\\\"')

    def format(self, strs, dict_param, is_shell_str=False):
        m = re.findall(r"{\w+}|\:\w+", strs, re.IGNORECASE | re.DOTALL)
        v = list()

        def lcmp(x, y):
            if len(x) > len(y):
                return -1
            else:
                return 1

        for i in m:
            key, num = re.subn(r"^'?\{|\}'?$|^\:", '', i)
            if is_shell_str:
                strs = strs.replace(i, self.format_shell_str(dict_param[key]))
            else:
                strs = strs.replace(i, dict_param[key])
        return strs

    def randstr(self, length=10):
        seq = [chr(x) for x in range(65, 91)]
        ret = []
        i = length
        while i > 0:
            i = i - 1
            ret.append(seq[random.randint(0, len(seq) - 1)])
        return ''.join(ret)

    def help(self):
        print(HELP_DOC)

    def get_hostname(self):
        os_name = os.name
        host_name = ""
        try:
            if os_name == 'nt':
                host_name = os.getenv('computername')
            elif os_name == 'posix':
                host = os.popen('hostname')
                try:
                    host_name = host.read().strip()
                except:
                    host_name = ''
                finally:
                    host.close()
            if host_name.strip() == '':
                host_name = socket.gethostbyname()
        except Exception as er:
            logger.error(er)
            return ""
        return host_name.strip()

    def _is_alive(self, port, address='127.0.0.1'):
        port = int(port)
        import socket
        s = socket.socket()
        try:
            s.settimeout(5)
            s.connect((address, port))
            return True
        except Exception as er:
            return False
        finally:
            try:
                s.close()
            except Exception as er:
                pass

    def check_port(self, port, address='127.0.0.1'):
        return self._is_alive(port, address)

    def _exec_filename(self):
        path = os.path.realpath(sys.path[0])
        if os.path.isfile(path):
            path = os.path.dirname(path)
            return os.path.abspath(path) + os.path.sep + __file__
        else:
            caller_file = inspect.stack()[1][1]
            return os.path.abspath(os.path.dirname(caller_file)) + os.path.sep + __file__

    def tuple2list(self, *args):
        print(args)
        l = []
        for i in args:
            l.append(i)
        return l

    def command_args(self, args):
        if isinstance(args, list) or isinstance(args, tuple):
            return '"%s"' % '" "'.join(args)
        else:
            return str(args)


class ZbxCommand(object):
    def __init__(self, cmd, is_log='0', task_id=''):
        mc = re.match('^su\s+[\'"a-zA-z09]+?\s+\-c', cmd)
        if PLATFORM == 'windows' and mc != None:
            cmd = cmd.replace(mc.group(0), '')
            cmd = cmd.strip()
            cmd = re.sub('^\"|\"$', '', cmd)
        self.cmd = cmd
        self.process = None
        self.is_log = is_log
        self.return_code = -1
        self.util = ZbxCommon()
        self.messge_success = ''
        self.message_error = ''
        self.result_lines = []
        if task_id == '':
            self.uuid = str(datetime.datetime.now()).replace(' ', '').replace(':', '').replace('-', '').replace('.', '')
        else:
            self.uuid = task_id + '_' + str(random.randint(0, 10)) + '.log'
        # self.uuid_error=self.uuid+'_error'
        self.fn = tempfile.gettempdir() + os.path.sep + self.uuid
        self.result = open(self.fn, 'a+')
        # self.result_error=open(tempfile.gettempdir()+ os.path.sep +self.uuid_error,'a+')

    def clean_log(self, task_id=''):
        try:
            if task_id == '':
                task_id = self.uuid
            tmpname = tempfile.gettempdir() + os.path.sep + task_id
            if os.path.exists(tmpname):
                with open(tmpname, 'r') as tf:
                    logger.info(tf.read())
                os.unlink(tmpname)
        except Exception as er:
            logger.error(er)

    def run(self, timeout=30, task_id='', url_success='', url_error='', url='', ip=''):
        def feedback(url, result, task_id, return_code=0, ip=''):
            try:
                if task_id == '' and url == '':
                    return
                machine_id = self.util.get_product_uuid()
                try:
                    if isinstance(result, bytes):
                        result = result.decode('utf-8', 'ignore')
                except Exception as er:
                    pass
                # if ip=='':
                #     ip=self.util.get_one_ip()
                data = self.util.url_fetch_witherr(url, {'cmd': self.cmd, 'machine_id': machine_id, 'result': result,
                                                         'task_id': task_id,
                                                         'success': self.messge_success, 'error': self.message_error,
                                                         'return_code': return_code, 'ip': machine_id,
                                                         's': self.util.get_hostname(), 'i': ip}, timeout=8)
                # print(data)
                if PY2:
                    if isinstance(data, str):
                        logger.info('feedback result:%s' + str(data))
                    if isinstance(data, unicode):
                        logger.info('feedback result:%s' + str(data.encode('utf-8', 'ignore')))
                if PY3:
                    if isinstance(data, str):
                        logger.info('feedback result:%s' + str(data))
            except Exception as er:
                data = {'task_id': task_id, 'result': result, 'url': url}
                logger.error('feedback error:\t' + str(er) + json.dumps(data))

        def target():
            if self.is_log == '1':
                logger.info("task_id:%s" % (task_id) + "\t" + str(self.cmd))
            elif self.is_log == '2':
                logger.info("task_id:%s" % (task_id) + "\t cmd:mask")

            self.process = subprocess.Popen(self.cmd, shell=True, stdout=self.result, stderr=self.result)
            self.process.communicate()
            self.process.poll()
            self.return_code = self.process.returncode
            if self.return_code == None:
                self.return_code = -1

        thread = threading.Thread(target=target)
        thread.start()
        st = time.time()
        bt = time.time()
        pos = 0

        def read_content(fn, start, end):
            with open(fn) as f:
                f.seek(start, 0)
                content = f.read(end - start)
                return content

        while True:
            if self.process == None:
                time.sleep(0.2)
            elif self.process.poll() == None:
                time.sleep(0.2)
            if self.process != None and self.process.poll() != None:
                break
            if timeout > 0 and time.time() - bt > timeout:
                break
            if time.time() - st > 1:
                st = time.time()
                fsize = os.path.getsize(self.fn)
                if fsize <= pos:
                    continue
                content = read_content(self.fn, pos, fsize)
                pos = fsize
                self.result_lines = []
                if url != '':
                    feedback(url, content, task_id, -2, ip)
                else:
                    feedback(self.util.get_server_uri('feedback_result2'), content, task_id, -2, ip)
                    # feedback(server_url+"/%s/%s"%(default_module,"feedback_result2"), content, task_id, -2,ip)
                time.sleep(0.2)
        content = read_content(self.fn, pos, os.path.getsize(self.fn))
        if len(content) > 0:
            feedback(self.util.get_server_uri('feedback_result2'), content, task_id, -2, ip)
            # feedback(server_url+"/%s/%s"%(default_module,"feedback_result2"), content, task_id, -2,ip)
            time.sleep(0.2)
        if timeout == -1 and self.process.poll() == None:
            thread.join()
        thread.join(timeout)

        def get_result():
            result = ''
            error = ''
            try:
                result = open(tempfile.gettempdir() + os.path.sep + self.uuid, 'r').read()
                if self.is_log == '1':
                    logger.info("task_id:%s\tSuccess Result:" % (task_id) + str(result))
                elif self.is_log == '2':
                    logger.info("task_id:%s\tSuccess Result:mask" % (task_id))
                elif self.is_log == '3':
                    logger.info("task_id:%s\tSuccess Result:" % (task_id) + str(result))
            except Exception as er:
                print(self.cmd)
                print('get_result:\t' + str(er))
                logger.error(er)
            finally:
                try:
                    if not self.result.closed:
                        self.result.close()
                    os.unlink(tempfile.gettempdir() + os.path.sep + self.uuid)
                except Exception as er:
                    print('get_result:\t' + str(er))
                    logger.error(er)
                    pass
            # try:
            #     error = open(tempfile.gettempdir() + os.path.sep + self.uuid_error, 'r').read()
            # except Exception as err:
            #     logger.error(er)
            #     print(err)
            #     if self.is_log == '1' or self.is_log == '2' or self.is_log == '3':
            #         logger.error("task_id:%s\tException Result:" % (task_id) + str(error))
            # finally:
            #     try:
            #         self.result_error.close()
            #         os.unlink(tempfile.gettempdir() + os.path.sep + self.uuid_error)
            #     except Exception as er:
            #         print('get_result close :\t' + str(er))
            #         logger.error(er)

            try:
                if PLATFORM == 'windows':
                    result = result.decode('gbk').encode('utf-8', 'ignore')
                    error = error.decode('gbk').encode('utf-8', 'ignore')
            except Exception as er:
                pass
            return result.strip(), error.strip()

        if thread.is_alive():
            logger.warn(self.cmd)
            result, error = get_result()
            if url != '':
                feedback(url, result, task_id, self.return_code, ip)
            if url_error != '':
                feedback(url_error, "(error)timeout\n%s" % (str(result) + str(error)), task_id, -1, ip)
                if self.is_log == '1' or self.is_log == '2' or self.is_log == '3':
                    logger.info("task_id:%s\ttimeout result has feedback to url:%s result:%s error:%s" % (
                    task_id, url_error, result, error))
            else:
                logger.info('timeout task_id:%s' % (task_id))
            try:
                self.process.terminate()
            except Exception as er:
                print(er)
            if result != '':
                return "(error)timeout \nresult:%s error:%s" % (str(result), str(error))
                # return result
            return "(error)timeout \nresult:%s error:%s" % (str(result), str(error))
            # util.url_fetch(server_url+'/slowlog',{'param':{ 'cmd':self.cmd,'ip':util.get_one_ip()}})
        result, error = get_result()
        try:
            if re.findall(r'\(error\)\s+file\s+not\s+found', result):
                self.return_code = 127
        except Exception as er:
            pass

        self.messge_success = result
        self.message_error = error

        if result == '' and error != '':
            result = error + "\nfinish"
        if url != '':
            logger.info(url)
            logger.info(result)
            feedback(url, result, task_id, self.return_code, ip)
            if self.is_log == '1' or self.is_log == '2' or self.is_log == '3':
                logger.info("task_id:%s\t result has feedback to url:%s " % (task_id, url))
        if self.return_code == 0 and url_success != '':
            feedback(url_success, result, task_id, self.return_code, ip)
            if self.is_log == '1' or self.is_log == '2' or self.is_log == '3':
                logger.info("task_id:%s\tsuccess result has feedback to url:%s " % (task_id, url_success))
        if self.return_code != 0 and url_error != '':
            feedback(url_error, result, task_id, self.return_code, ip)
            if self.is_log == '1' or self.is_log == '2' or self.is_log == '3':
                logger.info("task_id:%s\terror result has feedback to url:%s " % (task_id, url_error))
        if error.strip() != '':
            return result + "\n" + error
        else:
            return result


try:
    def quit(signum, frame):
        logger.warning("ctrl+c quit")
        sys.exit(1)


    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
except Exception as er:
    pass

cli = ZbxCommon()


class CAS(object):
    def __init__(self, objname=''):
        self.objname = objname
        self.id_key = '_id'
        self.version_key = '_version'
        self.status_key = '_status'

    def _check(self, obj):
        if obj == None or not isinstance(obj,
                                         dict) or not self.id_key in obj or not self.status_key in obj or not self.version_key in obj:
            return False, '%s %s %s must be in obj' % (self.version_key, self.id_key, self.status_key)
        return True, 'ok'

    def prepare(self, **kwargs):
        obj = None
        count = 1
        w = {self.status_key: 'idle'}
        kwargs.update(w)
        objs = cli.getobjs({'o': self.objname, 'limit': '%s' % (count), 'w': json.dumps(kwargs)})
        if cli.jq(objs, 'data,count') < count:
            return obj, 'resources not enough'
        rows = cli.jq(objs, 'data,rows')
        for row in rows:
            row[self.status_key] = 'hold'
            row2 = {}
            for k, v in row.items():
                row2[k] = v
            _id = row[self.id_key]
            _version = row[self.version_key]
            # row[self.version_key]=_version+1
            del row[self.id_key]
            row['last_update'] = int(time.time())
            data = cli.addobjs({'d': json.dumps(row), 'o': self.objname, 'w': json.dumps({self.id_key: _id,
                                                                                          self.status_key: 'idle',
                                                                                          self.version_key: _version})})
            if cli.jq(data, 'data,Updated') != None and cli.jq(data, 'data,Updated') > 0:
                row['_id'] = _id
                return row, 'ok'
        return obj, "not found"

    def cas(self, obj, orgin_status, target_status):
        ok, msg = self._check(obj)
        if not ok:
            return obj, msg
        objs = cli.getobjs({'o': self.objname, 'limit': '%s' % (1), 'w': json.dumps({self.status_key: orgin_status,
                                                                                     self.id_key: obj[self.id_key],
                                                                                     self.version_key: obj[
                                                                                         self.version_key]})})
        if cli.jq(objs, 'data,count') < 1:
            return obj, 'not found'
        rows = cli.jq(objs, 'data,rows')
        for row in rows:
            row.update(obj)
            row[self.status_key] = target_status
            _id = row[self.id_key]
            _version = row[self.version_key]
            row[self.version_key] = _version + 1
            del row[self.id_key]
            row['last_update'] = int(time.time())
            data = cli.addobjs({'d': json.dumps(row), 'o': self.objname, 'w': json.dumps({self.id_key: _id,
                                                                                          self.status_key: orgin_status,
                                                                                          self.version_key: _version})})
            if cli.jq(data, 'data,Updated') != None and cli.jq(data, 'data,Updated') > 0:
                row['_id'] = _id
                return row, 'ok'
        return obj, 'not found'

    def ready(self, obj):
        return self.cas(obj, 'hold', 'ready')

    def commit(self, obj):
        return self.cas(obj, 'ready', 'online')

    def rollback(self, obj):
        if self.status_key in obj and obj[self.status_key] in ['hold', 'ready']:
            return self.cas(obj, obj[self.status_key], 'idle')
        else:
            return obj, '_status must be hold or ready'

    def peek(self, **kwargs):
        objs = cli.getobjs({'o': self.objname, 'w': json.dumps(kwargs)})
        return cli.jq(objs, 'data,rows')


HELP_DOC = '''

        # from ops_channel import cli #导入包


        ##### 内置工具函数　#####
        # cli.args.get('name) #获取命令行参数
        # cli.id() #获取机器标识（uuid） 与  cli.get_machine_id() 相同
        # cli.get_machine_id() #获取机器标识（uuid）
        # cli.ip() #获取本机ip
        # cli.check_port(80,'127.0.0.1') #检查端口是否开启
        # cli.get_hostname() #获取本机主机名
        # cli.get_all_ip_list() #返回本机所有ip
        # cli.json_encode(data) #json编码
        # cli.json_decode(data) #json解码


        ##### 日期　#####
        # cli.date() #当时日期
        # cli.time() #当前时间
        # cli.now() #当前日期时间


        ##### 网络　#####
        # cli.get_server_uri('help') # 返回cli服务器url
        # cli.get('http://www.bb.com',timeout=2) #get获取网页，返回网页内容，注意错误处理
        # cli.post('http://test.web.com',{'name':'jqzhang'},timeout=2) #post获取网页 返回网页内容，注意错误处理

        #####  日志　#####
        # cli.log.info('message')  #打印提示日志
        # cli.log.error('message')  #打印错误日志

        #####  字符串与shell 　#####
        # cli.api({'i':'10.1.2.34','u':'java','sudo':'1','c':'ps aux','t':'20','async':'0','o':'json2'}) #远程执行命令
        # cli.rshell({'f':'filename','u':'java','sudo':'1','a':'argument','t':'20','async':'0','o':'json2'}) #远程执行脚本argument命令行参数
        # cli.execute('hostname',timeout=2) #本地执行命令
        # cli.join(['a','b','c'],sep=',') #数组并接，返回字符串
        # cli.jq({'data':{'rows':[{'id':1,'name':'hello'},{'id':2,'name':'world'}]}},'data,rows') #json 获取
        # cli.match('hello123world456','\d+') #正则匹配，返回数组
        # cli.split('hello123world456','\d+') #正则分割，返回数组
        # cli.getopt("cli api -u root --sudo 1 --token abc -c 'hostname' -t 5 ") #命令行参数获取，返回字典
        # cli.rand() #随机数，返回浮点数
        # cli.randint(1,100) #随机数，两者之间
        # cli.randstr(20) #随机字符串
        # cli.format('sadf {name} xxx',{'name':'jqzhang'}) #格式化，入参数为(str,dict) 返回字符串
        # print( cli.execute( cli.format('echo "{json}"|cli jq -k count',{'json':data},is_shell_str=True))) #python 与 shell交互
        # cli.login('username','passowrd') #登陆认证
        # cli.upload('/path/to/file','dir') #上传文件，需要登陆认证
        # cli.download('filename','dir(username)','/path/to/file') #下载文件 dir指的是登陆的用户名

        #####  cli数据接口　#####
        # cli.report({'data':{'name':'jqzhang','group':'devops'},'queue':'redis','topic':'test'}) #上报信息到redis
        # cli.get_report({'topic':'test'}) #获取上报信息
        # cli.addobjs({'o':'test','d':{'name':'jqzhang'},'w':{'name':'hello'}}) #增加对象到mongo  o  :表名 d:数据 w:条件
        # cli.getobjs({'o':'test','q':{'name':'jqzhang'},'c':'name,address','limit':'10'}) #增加对象到mongo  o:表名 q:查询条件 c:返回列名  limit:返回行数

        #####  cli通用命令行　#####
        #　说明：凡是能在shell中运行的cli用命令行的都可以通过 cli.xxx({}) 的方式进行调用
        #  举例：　shell：cli check -i 10.1.14.32    python: cli.check({'i':'10.1.14.32'})

'''

# if len(sys.argv)==2 and re.match('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}',sys.argv[1]):
#     cli.check_param(sys.argv[1])
