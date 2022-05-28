from functools import reduce
from typing import Mapping, Union, Optional

from hbutils.model import get_repr_info
from pysyslimit import SystemUser, SystemGroup


class Identification:
    def __init__(self, user=None, group=None, auto_group: bool = False):
        if user is not None:
            self.__user = SystemUser.loads(user)
        else:
            self.__user = None

        if group is not None:
            self.__group = SystemGroup.loads(group)
        elif auto_group and self.__user is not None:
            self.__group = self.__user.primary_group
        else:
            self.__group = None

    @property
    def user(self) -> SystemUser:
        return self.__user

    @property
    def group(self) -> SystemGroup:
        return self.__group

    def apply(self):
        if self.__group is not None:
            self.__group.apply()
        if self.__user is not None:
            self.__user.apply(include_group=False)

    def to_json(self) -> Mapping[str, Optional[Union[SystemUser, SystemGroup]]]:
        return {
            'user': self.user.name if self.user else None,
            'group': self.group.name if self.group else None,
        }

    @classmethod
    def current(cls) -> 'Identification':
        return cls.loads((SystemUser.current(), SystemGroup.current()))

    @classmethod
    def load_from_file(cls, filename: str) -> 'Identification':
        return cls.loads((SystemUser.load_from_file(filename),
                          SystemGroup.load_from_file(filename)))

    @classmethod
    def loads(cls, data) -> 'Identification':
        data = data or {}
        if isinstance(data, Identification):
            return data
        elif isinstance(data, dict):
            return cls(
                user=data.get('user', None),
                group=data.get('group', None),
                auto_group=False,
            )
        elif isinstance(data, tuple):
            _user, _group = data
            return cls(user=_user, group=_group, auto_group=False)
        elif isinstance(data, SystemUser):
            return cls(user=data, auto_group=True)
        elif isinstance(data, SystemGroup):
            return cls(user=None, group=data)
        else:
            try:
                return cls(user=SystemUser.loads(data), auto_group=True)
            except KeyError:
                raise ValueError('Unrecognized {actual} value for {cls}.'.format(
                    actual=repr(type(data)),
                    cls=repr(cls),
                ))

    @classmethod
    def merge(cls, *commands) -> 'Identification':
        def _merge(a: 'Identification', b: 'Identification') -> 'Identification':
            return cls(
                user=b.user or a.user,
                group=b.group or a.group,
            )

        # noinspection PyTypeChecker
        commands = [cls.loads(item) for item in commands]
        return reduce(_merge, commands, cls())

    def __tuple(self):
        _json = self.to_json()
        return _json['user'], _json['group']

    def __hash__(self):
        return hash(self.__tuple())

    def __eq__(self, other) -> bool:
        if other is self:
            return True
        elif isinstance(other, Identification):
            return other.to_json() == self.to_json()
        else:
            return False

    def __repr__(self) -> str:
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('user', (lambda: self.user.name, lambda: self.user)),
                ('group', (lambda: self.group.name, lambda: self.group)),
            ]
        )
