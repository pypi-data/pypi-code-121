# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
from shapelets.model import User, Group
from shapelets.services.base_service import BaseService


class Endpoint(Enum):
    USERS = "api/users"
    USERS_ME = f"{USERS}/me"
    USER_BY_ID = f"{USERS}/###subject_id###"
    GROUPS = "api/groups"

    def replace(self, subject_id: str):
        template = str(self.value)
        return template.replace("###subject_id###", subject_id)


class UsersService(BaseService):

    def get_users(self):
        users = self.request_get(Endpoint.USERS.value)
        return [User.from_dict(user) for user in users]

    def get_groups(self):
        groups = self.request_get(Endpoint.GROUPS.value)
        return [Group.from_dict(group) for group in groups]

    def get_my_user_details(self):
        user_me = self.request_get(Endpoint.USERS_ME.value)
        return User.from_dict(user_me)

    def get_user_details(self, subject_id: str):
        user = self.request_get(Endpoint.USER_BY_ID.replace(subject_id))
        return User.from_dict(user)
