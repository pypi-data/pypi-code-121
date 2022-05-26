# -*- coding: utf-8 -*-
from json.decoder import JSONDecodeError

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from ..base import Base
from ..models import Group
from ..utils.exceptions import AddComponentError


class Groups(Base):

    """Used to sync groups from a source instance to a destination instance of Swimlane"""

    def __get_destination_group(self, group: Group):
        try:
            return self.destination_instance.get_group_by_id(group.id)
        except JSONDecodeError as jd:
            self.log(f"Unable to find group '{group.name}' by id. Trying by name.")
        try:
            return self.destination_instance.get_group_by_name(group.name)
        except JSONDecodeError as jd:
            self.log(f"Unable to find group '{group.name}' by name. Assuming new group.")

    def __process_group(self, group: Group):
        if group.users:
            self.log(f"Checking user association on destination with group '{group.name}'.")
            user_list = []
            from .users import Users

            for user in group.users:
                _user = Users().sync_user(user_id=user.id)
                if _user:
                    user_list.append(_user)
            group.users = user_list

        if group.roles:
            self.log(f"Processing roles in role '{group.name}'")
            role_list = []
            from .roles import Roles

            for role in group.roles:
                _role = Roles().sync_role(role=role)
                if _role:
                    role_list.append(_role)
            group.roles = role_list
        return group

    def sync_group(self, group: Group):
        """This class syncs a single source instance group to a destination instance.

        We begin by processing the provided group and ensuring that all roles and users
        associated with the provided group are added to the destination instance.

        Once that is complete, we then sync any nested groups within the provided source instance group.

        If the provided group is already on the destination instance, then we just skip processing but if
        the provided group is not on the destination instance we add it.

        Args:
            group (Group): A source instance Group data model object.
        """
        if not self._is_in_include_exclude_lists(group.name, "groups") and group.name not in self.group_exclusions:
            self.log(f"Processing group '{group.name}' ({group.id})")
            group = self.__process_group(group=group)
            if group.groups:
                group_list = []
                for group_ in group.groups:
                    group_list.append(self.__process_group(group=group_))
                group.groups = group_list

            dest_group = self.__get_destination_group(group=group)

            if not dest_group:
                if not Base.dry_run:
                    self.log(f"Creating new group '{group.name}' on destination.")
                    dest_group = self.destination_instance.add_group(group)
                    if not dest_group:
                        raise AddComponentError(model=group, name=group.name)
                    self.log(f"Successfully added new group '{group.name}' to destination.")
                else:
                    self.add_to_diff_log(group.name, "added")
            else:
                self.log(f"Group '{group.name}' already exists on destination.")

    def sync(self):
        """This method is used to sync all groups from a source instance to a destination instance"""
        self.log(f"Attempting to sync groups from '{self.source_host}' to '{self.dest_host}'")
        groups = self.source_instance.get_groups()
        if groups:
            for group in groups:
                self.sync_group(group=group)
