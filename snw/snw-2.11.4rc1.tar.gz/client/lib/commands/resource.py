import os
import sys
from datetime import datetime

import requests
import six
from prettytable import PrettyTable

from lib.utils import write_to_stdout


class Resource:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def list(self):
        path = self.options.path
        if path and len(path.split(':')) != 2:
            raise ValueError('invalid path format: %s (should be storage:path)' % path)
        data = {'path': path, 'service': self.options.service}
        if "entity" in self.options and self.options.entity:
            data["entity"] = self.options.entity
        r = requests.get(os.path.join(self.options.url, "resource/list"), auth=self.auth, data=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'resource/list\' service: %s' % r.text)
        result = r.json()
        if not self.is_json:
            if self.options.path is None or self.options.path == '':
                res = PrettyTable(['Pool', 'Entity', 'Name', 'Type', 'Description'])
                res.align["Name"] = "l"
                res.align["Type"] = "l"
                res.align["Pool"] = "l"
                res.align["Description"] = "l"
                for r in result:
                    entity = r["entity"] if r["entity"] != "CONF_DEFAULT" else ""
                    res.add_row([r["pool"], entity, r["name"] + ":", r["type"], r["description"]])
            elif self.options.aggr:
                res = PrettyTable(['Type', 'Path', 'Suffixes'])
                res.align["Path"] = "l"
                res.align["Suffixes"] = "l"
                files = {}
                if not isinstance(result, list):
                    result = [result]
                for k in result:
                    if type(k) == dict:
                        k = k['key']
                    if k.endswith('/'):
                        res.add_row(['dir', k, ''])
                    else:
                        suffix = ""
                        if k.endswith(".gz"):
                            suffix = ".gz"
                            k = k[:-3]
                        p = k.rfind(".")
                        if p != -1:
                            suffix = k[p:] + suffix
                            k = k[:p]
                        if k not in files:
                            files[k] = []
                        files[k].append(suffix)
                for k, v in six.iteritems(files):
                    res.add_row(['file', k, ', '.join(sorted(v))])
            else:
                res = PrettyTable(['Type', 'Path', 'LastModified', 'Size (in byte)'])
                res.align["Path"] = "l"
                res.align["LastModified"] = "l"
                res.align["Size"] = "l"
                files = {}
                if not isinstance(result, list):
                    result = [result]
                for k in result:
                    meta = {}
                    if type(k) == dict:
                        meta = k
                        k = meta['key']
                    if k.endswith('/'):
                        res.add_row(['dir', k, '', ''])
                    else:
                        date = ''
                        if 'last_modified' in meta:
                            date = datetime.fromtimestamp(meta['last_modified']).strftime(
                                "%m/%d/%Y, %H:%M:%S")
                        size = ''
                        if 'size' in meta:
                            size = meta['size']
                        res.add_row(['file', k, date, size])
        else:
            res = result
        return res

    def get(self):
        params = {'path': self.options.path}
        if self.options.service is not None:
            params['service'] = self.options.service
        r = requests.get(os.path.join(self.options.url, "resource/file"),
                         auth=self.auth, params=params)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'resource/file\' service: %s' % r.text)
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:
                write_to_stdout(chunk)
        sys.exit(0)

    def execute_command(self):
        result = None
        if self.options.subcmd == "list":
            result = self.list()
        if self.options.subcmd == "get":
            result = self.get()
        return result
