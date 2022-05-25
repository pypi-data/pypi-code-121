import os

import requests
from prettytable import PrettyTable

import lib.utils as utils


class Role:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def list(self):
        status_code, result = utils.role_list(self.options.url, self.auth)
        if status_code != 200:
            raise RuntimeError(result)
        if not self.is_json:
            res = PrettyTable(["ID", "Name", "Permissions", "Shared with"])
            res.align["Name"] = "l"
            res.align["Permissions"] = "l"
            res.align["Shared with"] = "l"
            for r in result:
                name = r["name"]
                if "entity_code" in r:
                    name = r["entity_code"] + ":" + name
                permissions = []
                for p in r["permissions"]:
                    if "entity_code" in p:
                        permissions.append(p["entity_code"] + ":" + p["permission"])
                    else:
                        permissions.append(p["permission"])

                shared_entities = []
                for entity in r["shared_entities"]:
                    shared_entities.append(entity["code"] + "(" + entity["name"] + ")")

                res.add_row([r["id"], name, " ".join(permissions), " ".join(shared_entities)])
        else:
            res = result
        return res

    def get_data(self):
        data = {
            'name': self.options.name
        }
        if self.options.permissions is None:
            if self.options.subcmd == 'add':
                raise ValueError("missing permissions")
        else:
            data['permissions'] = []
            for p in self.options.permissions:
                psplit = p.split(':')
                if len(psplit) > 2:
                    raise ValueError("invalid format for permission: %s" % p)
                status, permission_id = utils.get_permission(self.options.url,
                                                             self.auth, psplit[-1])
                if not status:
                    raise RuntimeError(permission_id)
                data["permissions"].append({'permission': permission_id})
                if len(psplit) == 2:
                    status, entity_id = utils.get_entity(self.options.url, self.auth, psplit[0])
                    if not status:
                        raise RuntimeError(permission_id)
                    data["permissions"][-1]["entity"] = entity_id
        return data

    def send_data(self, data):
        r = requests.post(os.path.join(self.options.url, "role/" + self.options.subcmd),
                          auth=self.auth, json=data)
        if r.status_code != 200:
            raise RuntimeError(
                'incorrect result from \'role/%s\' service: %s' % (self.options.subcmd, r.text))
        res = 'ok'
        return res

    def add(self):
        data = self.get_data()

        status, entity_id = utils.get_entity(self.options.url, self.auth, self.options.entity)
        if not status:
            raise RuntimeError(entity_id)
        data['entity_id'] = entity_id

        res = self.send_data(data)
        return res

    def modify(self):
        data = self.get_data()

        status, role_id = utils.get_role(self.options.url, self.auth, self.options.role)
        if not status:
            raise RuntimeError(role_id)
        data['role_id'] = role_id

        res = self.send_data(data)
        return res

    def delete(self):
        data = {}

        status, role_id = utils.get_role(self.options.url, self.auth, self.options.role)
        if not status:
            raise RuntimeError(role_id)
        data['role_id'] = role_id

        res = self.send_data(data)
        return res

    def execute_command(self):
        result = None
        if self.options.subcmd == "list":
            result = self.list()
        if self.options.subcmd == "add":
            result = self.add()
        if self.options.subcmd == "modify":
            result = self.modify()
        if self.options.subcmd == "delete":
            result = self.delete()
        return result
