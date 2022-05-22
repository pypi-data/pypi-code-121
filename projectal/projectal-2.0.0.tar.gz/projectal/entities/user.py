from projectal import api
from projectal.entity import Entity
from projectal.linkers import *


class User(Entity, AccessPolicyLinker, PermissionLinker):
    """
    Implementation of the [User](https://projectal.com/docs/latest/#tag/User) API.
    """
    _path = 'user'
    _name = 'USER'

    @classmethod
    def register(cls, user):
        url = '/api/user/registration/{}'.format(user['uuId'])
        api.post(url, is_json=False)
        return True

    @classmethod
    def current_user_permissions(cls):
        """
        Get the authenticated user's permissions as a list.
        """
        return api.get('/api/user/permissions')['permissions']

    def bulk_user_link_permission(self, permission):
        self.__permission(self, permission, 'add')

    def bulk_user_unlink_permission(self, permission):
        self.__permission(self, permission, 'delete')

    @classmethod
    def __permission(cls, from_user, to_permission, operation):
        url = '/api/user/permission/{}'.format(operation)
        payload = [{
            'uuId': from_user['uuId'],
            'permissionList': [to_permission]
        }]
        api.post(url, payload=payload)
        return True

    @classmethod
    def current_user_details(cls):
        """Get some details about the authenticated user."""
        return api.get('/api/user/details')

    @classmethod
    def get_permissions(cls, user):
        """Get the permissions assigned to a specific User entity."""
        url = '/api/user/get/{}/permissions'.format(user['uuId'])
        return api.get(url)['data']
