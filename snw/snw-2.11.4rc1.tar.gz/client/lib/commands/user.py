import os
import re

import requests
from prettytable import PrettyTable

import lib.utils as utils


class User:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def list(self):

        r = requests.get(os.path.join(self.options.url, "user/list"), auth=self.auth,
                         params={'detail': True})
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'user/list\' service: %s' % r.text)
        result = r.json()
        if not self.is_json:
            res = PrettyTable(["ID", "TID", "Name", "Email", "Roles", "Groups"])
            res.align["Name"] = "l"
            for r in result:
                roles = []
                for role in r["roles"]:
                    if "entity_code" in role:
                        roles.append("%s:%s" % (role["entity_code"], role["name"]))
                    else:
                        roles.append(role["name"])
                groups = []
                for group in r["groups"]:
                    name = r["entity_code"] + ":" + group["name"]
                    groups.append(name)
                res.add_row([r["id"], r["tid"], r["name"], r["email"], " ".join(roles),
                             " ".join(groups)])
        else:
            res = result
        return res

    def add(self):
        if not re.match(r"^[A-Z]{3}$", self.options.user_code):
            raise ValueError('user_code should be [A-Z]{3}')
        status, entity_id = utils.get_entity(self.options.url, self.auth, self.options.entity)
        if not status:
            raise RuntimeError(entity_id)
        roles_id = []
        if self.options.roles is not None:
            for role in self.options.roles:
                status, role_id = utils.get_role(self.options.url, self.auth, role)
                if not status:
                    raise RuntimeError(role_id)
                roles_id.append(role_id)
        groups_id = []
        if self.options.groups is not None:
            for group in self.options.groups:
                status, group_id = utils.get_group(self.options.url, self.auth, group)
                if not status:
                    raise RuntimeError(group_id)
                groups_id.append(group_id)
        data = {
            'first_name': self.options.first_name,
            'last_name': self.options.last_name,
            'email': self.options.email,
            'password': self.options.password,
            'user_code': self.options.user_code,
            'entity_id': entity_id
        }
        r = requests.post(os.path.join(self.options.url, "user/add"), auth=self.auth, json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'user/add\' service: %s' % r.text)
        user_id = r.json()
        if self.options.roles is not None or self.options.groups is not None:
            data = {
                'user_id': user_id
            }

            if self.options.roles is not None:
                data['roles'] = roles_id
            if self.options.groups is not None:
                data['groups'] = groups_id

            r = requests.post(os.path.join(self.options.url, "user/modify"),
                              auth=self.auth, json=data)
            if r.status_code != 200:
                raise RuntimeError('incorrect result from \'user/modify\' service: %s' % r.text)
        res = "ok new user: email=%s -> id=%d" % (self.options.email, user_id)
        return res

    def modify(self):
        status, user_id = utils.get_user(self.options.url, self.auth, self.options.user)
        if not status:
            raise RuntimeError(user_id)
        data = {
            'user_id': user_id
        }
        if self.options.password is not None:
            data['password'] = self.options.password
        if self.options.first_name is not None:
            data['first_name'] = self.options.first_name
        if self.options.last_name is not None:
            data['last_name'] = self.options.last_name
        if self.options.roles is not None:
            roles_id = []
            for role in self.options.roles:
                status, role_id = utils.get_role(self.options.url, self.auth, role)
                if not status:
                    raise RuntimeError(role_id)
                roles_id.append(role_id)
            data['roles'] = roles_id
        if self.options.groups is not None:
            groups_id = []
            for group in self.options.groups:
                status, group_id = utils.get_group(self.options.url, self.auth, group)
                if not status:
                    raise RuntimeError(group_id)
                groups_id.append(group_id)
            data['groups'] = groups_id
        r = requests.post(os.path.join(self.options.url, "user/modify"), auth=self.auth, json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'user/modify\' service: %s' % r.text)
        res = 'ok'
        return res

    def delete(self):
        status, user_id = utils.get_user(self.options.url, self.auth, self.options.user)
        if not status:
            raise RuntimeError(user_id)
        data = {
            'user_id': user_id
        }
        r = requests.post(os.path.join(self.options.url, "user/delete"), auth=self.auth, json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'user/delete\' service: %s' % r.text)
        res = 'ok'
        return res

    def whoami(self):
        r = requests.get(os.path.join(self.options.url, "user/whoami"), auth=self.auth)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'user/whoami\' service: %s' % r.text)
        response = r.json()

        if not self.is_json:
            res = PrettyTable(["ID", "TID", "Name", "Email", "Roles", "Groups"])
            res.align["Name"] = "l"

            roles = []

            for role in response["roles"]:
                if "entity_code" in role:
                    roles.append("%s:%s" % (role["entity_code"], role["name"]))
                else:
                    roles.append(role["name"])
            groups = []
            for group in response["groups"]:
                name = response["entity_code"] + ":" + group["name"]
                groups.append(name)
            res.add_row([response["id"], response["tid"], response["name"], response["email"],
                         " ".join(roles), " ".join(groups)])
        else:
            res = response
        return res

    def password(self):
        data = {
            'password': self.options.password,
        }
        r = requests.post(os.path.join(self.options.url, "user/modify"), auth=self.auth, json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'user/modify\' service: %s' % r.text)
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
        if self.options.subcmd == "password":
            result = self.password()
        if self.options.subcmd == "delete":
            result = self.delete()
        if self.options.subcmd == "whoami":
            result = self.whoami()
        return result
