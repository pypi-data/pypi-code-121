# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum


class AttributeNames(Enum):
    EMAIL = "email"
    FAMILY_NAME = "familyName"
    FIRST_NAME = "firstName"
    NICKNAME = "nickName"
    UID = "uid"
    USER = "User"


class User:
    def __init__(self,
                 uid: str,
                 nick_name: str,
                 email: str,
                 first_name: str,
                 family_name: str):
        self.uid = uid
        self.nick_name = nick_name
        self.email = email
        self.first_name = first_name
        self.family_name = family_name

    def __repr__(self):
        s_repr = f"{AttributeNames.USER.value}({AttributeNames.UID.value}={self.uid}, "
        s_repr += f"{AttributeNames.NICKNAME.value}={self.nick_name}, "
        s_repr += f"{AttributeNames.EMAIL.value}={self.email}, "
        s_repr += f"{AttributeNames.FIRST_NAME.value}={self.first_name}, "
        s_repr += f"{AttributeNames.FAMILY_NAME.value}={self.family_name})"
        return s_repr

    def to_dict(self):
        return {
            AttributeNames.UID.value: self.uid,
            AttributeNames.NICKNAME.value: self.nick_name,
            AttributeNames.EMAIL.value: self.email,
            AttributeNames.FIRST_NAME.value: self.first_name,
            AttributeNames.FAMILY_NAME.value: self.family_name
        }

    @staticmethod
    def from_dict(dct: dict):
        return User(
            uid=dct[AttributeNames.UID.value],
            nick_name=dct[AttributeNames.NICKNAME.value],
            email=dct[AttributeNames.EMAIL.value],
            first_name=dct[AttributeNames.FIRST_NAME.value],
            family_name=dct[AttributeNames.FAMILY_NAME.value])
