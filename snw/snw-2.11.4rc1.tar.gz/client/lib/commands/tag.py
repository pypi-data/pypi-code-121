import logging
import os

import requests
from prettytable import PrettyTable

import client.launcher as launcher

launcher.LOGGER = logging.getLogger()


class Tag:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def list(self):
        r = requests.get(os.path.join(self.options.url, "model/tags"), auth=self.auth)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'tag/list\' service: %s' % r.text)
        result = r.json()
        if not self.is_json:
            res = PrettyTable(["Name", "Entity"])
            res.align["Name"] = "l"
            for r in result:
                res.add_row([r["tag"], r["entity"]])
        else:
            res = result
        return res

    def delete(self):
        r = requests.delete(os.path.join(self.options.url, "model/tag"), auth=self.auth,
                            params={'tag': self.options.name})
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'tag/delete\' service: %s' % r.text)
        res = 'ok delete tag %s' % self.options.name
        return res

    def add(self):
        r = requests.put(os.path.join(self.options.url, "model/tag"), auth=self.auth,
                         params={'tag': self.options.name})
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'tag/add\' service: %s' % r.text)
        tag = r.json()
        res = "ok new tag: name=%s, entity=%s, creator=%s" % (
            tag['tag'], tag['entity'], tag['creator'])
        return res

    def detail(self):
        r = requests.get(os.path.join(self.options.url, "model/tags", self.options.name),
                         auth=self.auth)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'tag/detail\' service: %s' % r.text)
        result = r.json()
        if not self.is_json:
            res = PrettyTable(["Name", "Entity", "Creator", "Models"])
            res.align["Name"] = "l"
            model_name = ""
            if "models" in result:
                model_name = ",".join(result["models"])
            res.add_row([result["tag"], result["entity"], result["creator"], model_name])
        else:
            res = result
        return res

    def modify(self):
        r = requests.post(os.path.join(self.options.url, "model/tag"), auth=self.auth,
                          params={'tag': self.options.name, 'newTag': self.options.newname})
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'tag/modify\' service: %s' % r.text)
        res = 'ok modify tag %s to %s' % (self.options.name, self.options.newname)
        return res

    def execute_command(self):
        result = None
        if self.options.subcmd == "add":
            result = self.add()
        if self.options.subcmd == "list":
            result = self.list()
        if self.options.subcmd == "detail":
            result = self.detail()
        if self.options.subcmd == "delete":
            result = self.delete()
        if self.options.subcmd == "modify":
            result = self.modify()
        return result
