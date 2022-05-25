import os
import time
from datetime import datetime
import requests
from prettytable import PrettyTable


class Docker:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def list(self):
        r = requests.get(os.path.join(self.options.url, "docker/list"),
                         auth=self.auth, params={'docker': self.options.docker})
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'docker/list\' service: %s' % r.text)
        result = r.json()
        if not self.is_json:
            res = PrettyTable(["Date", "IMAGE", "Tag", "Configurations"])
            res.align["Configurations"] = "l"
            for r in sorted(result, key=lambda r: time.mktime(
                    datetime.strptime(r['date'].rstrip(' GMT'), "%a, %d %b %Y %H:%M:%S").timetuple())):
                d = r["date"]
                imgtag = r["image"].split(':')
                res.add_row([d, imgtag[0], imgtag[1], r["configs"]])
        else:
            res = result
        return res

    def add(self):
        data = {
            'image': self.options.image
        }

        if not os.path.exists(self.options.configs):
            raise RuntimeError('%s is not a file.' % self.options.configs)

        if not os.path.exists(self.options.schema):
            raise RuntimeError('%s is not a file.' % self.options.schema)

        with open(self.options.configs) as cfile:
            data['configs'] = cfile.read()

        with open(self.options.schema) as sfile:
            data['schema'] = sfile.read()

        r = requests.post(os.path.join(self.options.url, "docker/add"), auth=self.auth, data=data)

        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'docker/add\' service: %s' % r.text)

        res = 'ok'
        return res

    def describe(self):
        image = self.options.docker
        p = image.find(":")
        tag = image[p + 1:]
        image = image[:p]
        assert self.options.config, "docker describe requires --config parameter"
        r = requests.get(os.path.join(self.options.url, "docker/describe"),
                         params={'config': self.options.config, 'image': image, 'tag': tag},
                         auth=self.auth)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'service/describe\' service: %s' % r.text)
        res = r.json()
        return res

    def execute_command(self):
        result = None
        if self.options.subcmd == "list":
            result = self.list()
        if self.options.subcmd == "add":
            result = self.add()
        if self.options.subcmd == "describe":
            result = self.describe()
        return result
