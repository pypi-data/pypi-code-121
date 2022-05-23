from testlodge.client.base import BaseClient
from testlodge.client.custom_field import CustomFieldClient
from testlodge.client.project import ProjectClient
from testlodge.client.user import UserClient


class Client(UserClient, ProjectClient, CustomFieldClient, BaseClient):
    ...


__all__ = ['Client']
