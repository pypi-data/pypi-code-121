import os

import requests
from prettytable import PrettyTable

import lib.utils as utils


class Group:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def list(self):
        status_code, result = utils.group_list(self.options.url, self.auth)
        if status_code != 200:
            raise RuntimeError(result)
        if not self.is_json:
            res = PrettyTable(["ID", "Name", "Roles", "Users"])
            res.align["Name"] = "l"
            res.align["Roles"] = "l"
            res.align["Users"] = "l"
            for g in result:
                name = g["entity_code"] + ":" + g["name"]
                roles = []
                for r in g["roles"]:
                    if "entity_code" in r:
                        roles.append(r["entity_code"] + ":" + r["name"])
                    else:
                        roles.append(r["name"])
                users = []
                for u in g["users"]:
                    u["name"] = u["first_name"] + " " + u["last_name"]
                    users.append(u["tid"] + "(" + u["name"] + ")")
                res.add_row([g["id"], name, " ".join(roles), " ".join(users)])
        else:
            res = result
        return res

    def send_data(self, data):
        r = requests.post(os.path.join(self.options.url, "group/" + self.options.subcmd),
                          auth=self.auth, json=data)
        if r.status_code != 200:
            raise RuntimeError(
                'incorrect result from \'group/%s\' service: %s' % (self.options.subcmd, r.text))
        res = 'ok'
        return res

    def get_data(self):
        data = {
            'name': self.options.name
        }
        if self.options.users is not None:
            users_id = []
            for user in self.options.users:
                status, user_id = utils.get_user(self.options.url, self.auth, user)
                if not status:
                    raise RuntimeError(user_id)
                users_id.append(user_id)
            data['users'] = users_id
        if self.options.roles is not None:
            roles_id = []
            for role in self.options.roles:
                status, role_id = utils.get_role(self.options.url, self.auth, role)
                if not status:
                    raise RuntimeError(role_id)
                roles_id.append(role_id)
            data['roles'] = roles_id
        return data

    def add(self):
        data = self.get_data()
        if self.options.entity is not None:
            status, entity_id = utils.get_entity(self.options.url, self.auth, self.options.entity)
            if not status:
                raise RuntimeError(entity_id)
            data['entity_id'] = entity_id

        res = self.send_data(data)

        return res

    def modify(self):
        data = self.get_data()
        status, group_id = utils.get_group(self.options.url, self.auth, self.options.group)
        if not status:
            raise RuntimeError(group_id)
        data['group_id'] = group_id

        res = self.send_data(data)

        return res

    def delete(self):
        data = {}
        status, group_id = utils.get_group(self.options.url, self.auth, self.options.group)
        if not status:
            raise RuntimeError(group_id)
        data['group_id'] = group_id

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
