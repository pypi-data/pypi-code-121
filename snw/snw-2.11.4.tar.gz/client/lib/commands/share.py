import logging
import os

import requests

import client.launcher as launcher
from lib import utils

launcher.LOGGER = logging.getLogger()


class Share:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def add(self):
        data = {"roles": []}
        for role in self.options.roles:
            status, role_id = utils.get_role(self.options.url, self.auth, role)
            if not status:
                raise RuntimeError(role_id)
            data['roles'].append(role_id)
        status, src_entity_id = utils.get_entity(self.options.url, self.auth,
                                                 self.options.src_entity)
        if not status:
            raise RuntimeError(src_entity_id)
        data['src_entity_id'] = src_entity_id
        status, dest_entity_id = utils.get_entity(self.options.url, self.auth,
                                                  self.options.dest_entity)
        if not status:
            raise RuntimeError(dest_entity_id)
        data['dest_entity_id'] = dest_entity_id
        r = requests.post(os.path.join(self.options.url, "role/share/add"),
                          auth=self.auth, json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'role/share/add\' service: %s' % r.text)
        res = 'ok'
        return res

    def delete(self):
        data = {}
        status, src_entity_id = utils.get_entity(self.options.url, self.auth,
                                                 self.options.src_entity)
        if not status:
            raise RuntimeError(src_entity_id)
        data['src_entity_id'] = src_entity_id
        status, dest_entity_id = utils.get_entity(self.options.url, self.auth,
                                                  self.options.dest_entity)
        if not status:
            raise RuntimeError(dest_entity_id)
        data['dest_entity_id'] = dest_entity_id
        for role in self.options.roles:
            status, role_id = utils.get_role(self.options.url, self.auth, role)
            if not status:
                raise RuntimeError(role_id)
            data['role_id'] = role_id
            r = requests.post(os.path.join(self.options.url, "role/share/remove"),
                              auth=self.auth, json=data)
            if r.status_code != 200:
                raise RuntimeError(
                    'incorrect result from \'role/share/remove\' service: %s' % r.text)
        res = 'ok'
        return res

    def execute_command(self):
        result = None
        if self.options.subcmd == "add":
            result = self.add()
        if self.options.subcmd == "delete":
            result = self.delete()
        return result
