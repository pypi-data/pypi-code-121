# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum


class AttributeNames(Enum):
    DIMS = 'dims'
    EXCEPTION = "unrecognized type"
    IS_USER = "isUser"
    OWNER = "owner"
    PRIVILEGE = "privilege"
    READER = "reader"
    SID = "sid"
    WRITER = "writer"


class Permission(Enum):
    READER = 1
    WRITER = 2
    OWNER = 3

    @staticmethod
    def to_string(permission_type):
        if permission_type == Permission.READER:
            return AttributeNames.READER.value
        if permission_type == Permission.WRITER:
            return AttributeNames.WRITER.value
        if permission_type == Permission.OWNER:
            return AttributeNames.OWNER.value
        raise ValueError(f"{AttributeNames.EXCEPTION.value}: {permission_type}")

    @staticmethod
    def from_string(permission_type):
        if permission_type == AttributeNames.READER.value:
            return Permission.READER
        if permission_type == AttributeNames.WRITER.value:
            return Permission.WRITER
        if permission_type == AttributeNames.OWNER.value:
            return Permission.OWNER
        raise ValueError(f"{AttributeNames.EXCEPTION.value}: {permission_type}")


class Privilege:
    def __init__(self,
                 sid: str,
                 is_user: bool,
                 privilege: Permission):
        self.sid = sid
        self.is_user = is_user
        self.privilege = privilege

    def __repr__(self):
        return (f"{AttributeNames.PRIVILEGE.value.capitalize()}({AttributeNames.SID.value}={self.sid},"
                f" {AttributeNames.IS_USER.value}={self.is_user}, "
                f"{AttributeNames.PRIVILEGE.value}={self.privilege})")

    def to_dict(self):
        return {
            AttributeNames.SID.value: self.sid,
            AttributeNames.IS_USER.value: self.is_user,
            AttributeNames.PRIVILEGE.value: Permission.to_string(self.privilege)
        }

    @staticmethod
    def from_dict(dct: dict):
        return Privilege(
            sid=dct[AttributeNames.SID.value],
            is_user=dct[AttributeNames.IS_USER.value],
            privilege=Permission.from_string(dct[AttributeNames.PRIVILEGE.value]))
