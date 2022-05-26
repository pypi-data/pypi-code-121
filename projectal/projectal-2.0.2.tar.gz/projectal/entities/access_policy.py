from projectal.entity import Entity
from projectal.linkers import PermissionLinker


class AccessPolicy(Entity, PermissionLinker):
    """
    Implementation of the [Access Policy](https://projectal.com/docs/latest/#tag/Access-Policy) API.
    """
    _path = 'access-policy'
    _name = 'ACCESS_POLICY'