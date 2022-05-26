# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from ..base import Base
from ..models import Role
from ..utils.exceptions import AddComponentError


class Roles(Base):

    """Used to sync roles from a source instance to a destination instance of Swimlane"""

    def __process_role(self, role: Role):
        if role.users:
            self.log(f"Processing users in role '{role.name}'")
            user_list = []
            from .users import Users

            for user in role.users:
                _user = Users().sync_user(user_id=user.id)
                if _user:
                    user_list.append(_user)
            role.users = user_list
        if role.groups:
            self.log(f"Processing groups in role '{role.name}'")
            group_list = []
            from .groups import Groups

            for group in role.groups:
                _group = Groups().sync_group(group=group)
                if _group:
                    group_list.append(_group)
            role.groups = group_list
        return role

    def sync_role(self, role: Role):
        if not self._is_in_include_exclude_lists(role.name, "roles") and role.name not in self.role_exclusions:
            self.log(f"Processing role '{role.name}' ({role.id})")
            role = self.__process_role(role=role)
            dest_role = self.destination_instance.get_role(role_id=role.id)
            if not dest_role:
                if not Base.dry_run:
                    self.log(f"Creating new role '{role.name}' on destination.")
                    dest_role = self.destination_instance.add_role(role)
                    if not dest_role:
                        raise AddComponentError(model=role, name=role.name)
                    self.log(f"Successfully added new role '{role.name}' to destination.")
                    return dest_role
                else:
                    self.add_to_diff_log(role.name, "added")
            else:
                self.log(f"Role '{role.name}' already exists on destination.")

    def sync(self):
        """This method is used to sync all roles from a source instance to a destination instance"""
        self.log(f"Attempting to sync roles from '{self.source_host}' to '{self.dest_host}'")
        roles = self.source_instance.get_roles()
        if roles:
            for role in roles:
                self.sync_role(role=role)
