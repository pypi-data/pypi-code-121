# -*- coding: utf-8 -*-
from typing import AnyStr, List

from attr import define, field

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from .base import CreatedByUser


@define
class UserLight:
    id: AnyStr = field()
    name: AnyStr = field()
    disabled: bool = field()

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="UserLight")


@define
class User(UserLight):
    """A Swimlane User object model"""

    active: bool = field()
    displayName: AnyStr = field()
    firstName: AnyStr = field()
    isLdapUser: bool = field()
    isOTPVerified: bool = field()
    isOtpEnforced: bool = field()
    isOtpExempted: bool = field()
    isOtpUser: bool = field()
    isSystemUser: bool = field()
    lastPasswordChangedDate: AnyStr = field()
    sessionTimeoutType: AnyStr = field()
    timeZoneId: AnyStr = field()
    passwordComplexityScore: int = field()
    passwordResetRequired: bool = field()

    currentFailedLogInAttempts: int = field(default=None)
    isLocked: bool = field(default=None)
    avatar: AnyStr = field(default=None)
    userName: AnyStr = field(default=None)
    email: AnyStr = field(default=None)
    lastName: AnyStr = field(default=None)
    middleInitial: AnyStr = field(default=None)
    lastLogin: AnyStr = field(default=None)
    primaryGroup: CreatedByUser = field(default={})
    createdByUser: CreatedByUser = field(default={})
    createdDate: AnyStr = field(default="")
    modifiedByUser: CreatedByUser = field(default={})
    modifiedDate: AnyStr = field(default="")
    favorites: dict = field(default={})
    permissions: dict = field(default={})
    roles: List = field(default=[])
    groups: List = field(default=[])
    phoneNumber: AnyStr = field(default=None)
    lastFailedLogInAttemptAt: AnyStr = field(default=None)

    def __init__(self, **kwargs):
        from ..base import Base
        from ..utils.exceptions import ModelError

        Base().scrub(kwargs)
        try:
            self.__attrs_init__(**kwargs)
        except TypeError as te:
            raise ModelError(err=te, name="User")

    def __attrs_post_init__(self):
        if self.roles:
            role_list = []
            from .role import Role

            for role in self.roles:
                try:
                    role_list.append(Role(**role))
                except Exception as e:
                    raise e
            self.roles = role_list
        if self.groups:
            from .group import Group

            group_list = []
            for group in self.groups:
                try:
                    group_list.append(Group(**group))
                except Exception as e:
                    raise e
            self.groups = group_list
