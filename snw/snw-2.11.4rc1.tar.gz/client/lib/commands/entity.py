import os
import re

import requests
from prettytable import PrettyTable

import lib.utils as utils


class Entity:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def list(self):
        r = requests.get(os.path.join(self.options.url, "entity/list"),
                         auth=self.auth, params={"detail": True, "all": self.options.all})
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'entity/list\' service: %s' % r.text)
        result = r.json()
        if not self.is_json:
            row = ["ID", "Code", "Name", "Email", "Description"]
            if self.options.all:
                row.append("Active")
            res = PrettyTable(row)
            for r in sorted(result, key=lambda r: r["id"]):
                r_row = [r["id"], r["entity_code"], r["name"], r["email"], r["description"]]
                if self.options.all:
                    r_row.append(r["active"])
                res.add_row(r_row)
        else:
            res = result
        return res

    def send_data(self, data):
        r = requests.post(os.path.join(self.options.url, "entity/" + self.options.subcmd),
                          auth=self.auth, json=data)
        if r.status_code != 200:
            raise RuntimeError(
                'incorrect result from \'entity/%s\' service: %s' % (self.options.subcmd, r.text))
        return r

    def add(self):
        data = {
            'name': self.options.name,
            'email': self.options.email,
            'tel': self.options.tel,
            'address': self.options.address,
            'description': self.options.description
        }

        if not re.match(r"^[A-Z]{2}$", self.options.entity_code):
            raise ValueError('entity_code should be [A-Z]{2}')
        data['entity_code'] = self.options.entity_code

        r = self.send_data(data)
        res = "ok new entity: name=%s -> id=%d" % (self.options.name, r.json())
        return res

    def modify(self):
        data = {
            'name': self.options.name,
            'email': self.options.email,
            'tel': self.options.tel,
            'address': self.options.address,
            'description': self.options.description
        }

        status, entity_id = utils.get_entity(self.options.url, self.auth, self.options.entity)
        if not status:
            raise RuntimeError(entity_id)
        data['entity_id'] = entity_id

        r = self.send_data(data)
        res = 'ok'
        return res

    def disable(self):
        data = {}

        status, entity_id = utils.get_entity(self.options.url, self.auth, self.options.entity)
        if not status:
            raise RuntimeError(entity_id)
        data['entity_id'] = entity_id

        r = self.send_data(data)
        res = 'ok'
        return res

    def enable(self):
        data = {}

        status, entity_id = utils.get_entity(self.options.url, self.auth, self.options.entity)
        if not status:
            raise RuntimeError(entity_id)
        data['entity_id'] = entity_id

        r = self.send_data(data)
        res = 'ok'
        return res

    def execute_command(self):
        result = None
        if self.options.subcmd == "list":
            result = self.list()
        if self.options.subcmd == "add":
            result = self.add()
        if self.options.subcmd == "modify":
            result = self.modify()
        if self.options.subcmd == "disable":
            result = self.disable()
        if self.options.subcmd == "enable":
            result = self.enable()
        return result
