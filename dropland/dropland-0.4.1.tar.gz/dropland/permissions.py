from abc import ABC, abstractmethod
from inspect import isclass
from typing import List, Callable, Set, Tuple, Optional, Union, Type


class BasePermission(ABC):
    depends_on = []

    @classmethod
    @abstractmethod
    def has_permissions(cls, *args, **kwargs) -> bool:
        raise NotImplementedError

    # noinspection PyMethodMayBeStatic
    def has_object_permissions(self, *args, **kwargs) -> bool:
        return False


PermissionType = Union[Type, object, Callable[..., bool]]


class PermissionChecker:
    def __init__(self, permissions: List[PermissionType]):
        self.permissions = permissions

    def _check_permission(self, permission: PermissionType,
                          perms_cache: Set[str], *args, **kwargs) -> Tuple[bool, Optional[PermissionType]]:
        perm_name = None

        if isclass(permission):
            curr_deps = list(getattr(permission, 'depends_on', []))
            perm_name = '.'.join([permission.__module__, permission.__qualname__])

            if perm_name in perms_cache:
                return True, None

            for dep_permission in curr_deps:
                if not self._check_permission(dep_permission, perms_cache, *args, **kwargs):
                    return False, dep_permission

        elif hasattr(permission, '__name__'):
            perm_name = permission.__name__

        if isclass(permission):
            if issubclass(permission, BasePermission):
                if not permission.has_permissions(*args, **kwargs):
                    return False, permission
        elif isinstance(permission, BasePermission):
            if not permission.has_object_permissions(*args, **kwargs):
                return False, permission
        elif not permission(*args, **kwargs):
            return False, permission

        if perm_name:
            perms_cache.add(perm_name)

        return True, None

    def __call__(self, *args, **kwargs) -> Tuple[bool, Optional[PermissionType]]:
        perms_cache: Set[str] = set()

        for permission in self.permissions:
            res, error_callable = self._check_permission(permission, perms_cache, *args, **kwargs)
            if not res:
                return False, error_callable
        return True, None
