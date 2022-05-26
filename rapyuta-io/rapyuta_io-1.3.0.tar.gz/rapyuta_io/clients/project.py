from __future__ import absolute_import
import re

import enum

import six

from rapyuta_io.clients.organization import Organization
from rapyuta_io.utils import RestClient, InvalidParameterException
from rapyuta_io.utils.object_converter import ObjBase, list_field, nested_field
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.utils import create_auth_header, get_api_response_data

project_name_regex = re.compile('^[a-z0-9-]{3,15}$')


class Project(ObjBase):
    """
    Project is an organizational unit and all the resources must belong to a Project.

    :ivar id: id of the Project
    :vartype id: int
    :ivar guid: guid of the Project
    :vartype guid: str
    :ivar created_at: creation time of the Project
    :vartype created_at: str
    :ivar updated_at: updation time of the Project
    :vartype updated_at: str
    :ivar deleted_at: deletion time of the Project
    :vartype deleted_at: str
    :param name: name of the Project
    :type name: str
    :ivar creator: GUID of the User that created the Project
    :vartype creator: str
    :ivar users: Users that have access to the Project
    :vartype users:   list(:py:class:`~rapyuta_io.clients.project.User`)
    :ivar organization: Organization that the project belongs to
    :vartype organization: :py:class:`~rapyuta_io.clients.organization.Organization`
    """
    PROJECT_PATH = '/api/project'

    def __init__(self, name, organization_guid=None):
        self.validate(name, organization_guid)
        self.name = name
        self.id = None
        self.guid = None
        self.created_at = None
        self.updated_at = None
        self.deleted_at = None
        self.creator = None
        self.users = None
        org = None
        if organization_guid is not None:
            org = Organization()
            setattr(org, 'guid', organization_guid)
        self.organization = org

    def get_deserialize_map(self):
        return {
            'id': 'ID',
            'guid': 'guid',
            'created_at': 'CreatedAt',
            'updated_at': 'UpdatedAt',
            'deleted_at': 'DeletedAt',
            'name': 'name',
            'creator': 'creator',
            'users': list_field('users', User),
            'organization': nested_field('organization', Organization)
        }

    def get_serialize_map(self):
        serialized_project = {
            'name': 'name',
        }
        if self.organization is not None:
            serialized_project['organization'] = 'organization'
        return serialized_project

    @staticmethod
    def validate(name, organization_guid):
        if not isinstance(name, str):
            raise InvalidParameterException('name must be a string')
        length = len(name)
        if length < 3 or length > 15:
            raise InvalidParameterException('length of name must be between 3 and 15 characters')
        if organization_guid is not None and not isinstance(organization_guid, six.string_types):
            raise InvalidParameterException('organization_guid needs to a non empty string')
        if not project_name_regex.match(name):
            raise InvalidParameterException('name can have alphabets, numbers or - only')

    def delete(self):

        """
        Delete the project using the project object.

        Following example demonstrates how to delete a project using project object:

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> project = client.get_project(guid='project-id')
        >>> project.delete()

        """

        if not (hasattr(self, '_core_api_host') and hasattr(self, '_auth_token')):
            raise InvalidParameterException('Project must be created first')
        url = self._core_api_host + self.PROJECT_PATH + '/delete'
        headers = create_auth_header(self._auth_token, self.guid)
        payload = {'guid': self.guid}
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute(payload)
        get_api_response_data(response, parse_full=True)


class User(ObjBase):
    """
    User is the representation of a Human user on the Platform. Users can be part of one of more Projects.

    :ivar guid: guid of the User
    :vartype guid: str
    :ivar first_name: First name of the User
    :vartype first_name: str
    :ivar last_name: Last name of the User
    :vartype last_name: str
    :ivar email_id: Email of the User
    :vartype email_id: str
    :ivar state: The state of the User on the Platform
    :vartype state: :py:class:`~rapyuta_io.clients.project.UserState`
    :ivar projects: Projects to which the User Belongs
    :vartype projects:   list(:py:class:`~rapyuta_io.clients.project.Project`)
    :ivar organization: Primary organization that the user created or got invited to for the first time
    :vartype organization:  :py:class:`~rapyuta_io.clients.organization.Organization`
    :ivar organizations: List of organizations that the user is part of
    :vartype organizations:  list(:py:class:`~rapyuta_io.clients.organization.Organization`)
    """
    def __init__(self):
        self.guid = None
        self.first_name = None
        self.last_name = None
        self.email_id = None
        self.state = None
        self.projects = None
        self.organization = None
        self.organizations = None

    def get_deserialize_map(self):
        return {
            'guid': 'guid',
            'first_name': 'firstName',
            'last_name': 'lastName',
            'email_id': 'emailID',
            'state': 'state',
            'projects': list_field('projects', Project),
            'organization': nested_field('organization', Organization),
            'organizations': list_field('organizations', Organization),
        }

    def get_serialize_map(self):
        pass


class UserState(str, enum.Enum):
    """
    Enumeration variables for UserState.

    UserState can be any of the following types \n

    UserState.REGISTERED ('REGISTERED') \n
    UserState.ACTIVATED ('ACTIVATED') \n
    UserState.DEACTIVATED ('DEACTIVATED') \n
    UserState.SUSPENDED ('SUSPENDED') \n
    UserState.INVITED ('INVITED') \n
    """

    def __str__(self):
        return str(self.value)

    REGISTERED = 'REGISTERED'
    ACTIVATED = 'ACTIVATED'
    DEACTIVATED = 'DEACTIVATED'
    SUSPENDED = 'SUSPENDED'
    INVITED = 'INVITED'
