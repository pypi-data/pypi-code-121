import re

import tenacity
from geodesic.bases import APIObject
from geodesic.account import User
from geodesic import raise_on_error
from geodesic.descriptors import BaseDescr, RegexDescr, StringDescr
from geodesic.service import ServiceClient

from typing import Union
from functools import lru_cache

# Projects client
projects_client = ServiceClient("krampus", 1, "projects")
project_name_re = re.compile(r'^(\w+[\w\-\_]*|\*)$')


@lru_cache(maxsize=None)
def _get_project(name_or_uid: str = None):
    """
    Gets a project by name or uid. It's always
    better to specify the uid to avoid ambiguity.
    The name will be used to find a project that
    the user owns, but won't check other projects
    that the name might match

    Args:
        name_or_uid: the name or uid of the project.
    """
    res = raise_on_error(projects_client.get(name_or_uid))
    p = res.json()['project']
    if p is None:
        return None
    return Project(**p)


def get_project(name_or_uid: str = None, refresh: bool = False):
    """
    Gets a project by name or uid. It's always
    better to specify the uid to avoid ambiguity.
    The name will be used to find a project that
    the user owns, but won't check other projects
    that the name might match

    Args:
        name_or_uid: the name or uid of the project.
        refresh: projects are cached by default. If you want the latest
            list from the server, set refresh to True
    """
    if refresh:
        _get_project.cache_clear()
    return _get_project(name_or_uid)


def get_projects():
    res = raise_on_error(projects_client.get(''))
    return [Project(**p) for p in res.json()['projects']]


def create_project(name: str, alias: str, description: str, keywords: list = []) -> 'Project':
    """Creates a new project. Helpful instead of creating a Project instance directly.

    Args:
        name: name of the project. Used in most cases to look up a project
        alias: a human readable name for the project
        description: a text description of this project
        keywords: a list of keywords to describe this project.
    """
    project = Project(name=name, alias=alias, description=description, keywords=keywords)
    project.create()
    return project


class Project(APIObject):
    """The Project class to manage groups of nodes in a subgraph in entanglement

    Args:
        **project: metadata about a particular project
    """
    uid = StringDescr(doc="unique ID set by the system")
    name = RegexDescr(regex=project_name_re, doc="the name of this project, unique to the user")
    alias = StringDescr(doc="a human readable name for this project/subgraph")
    description = StringDescr(doc="a description of this project/subgraph")
    owner = StringDescr(doc="the subject (user id) of this owner of this project")

    def __init__(self, **project):
        self._client = projects_client
        super().__init__(self, **project)

    def create(self) -> None:
        """
        Creates new project for this object
        """
        raise_on_error(self._client.post("", project=self))

        @tenacity.retry(wait=tenacity.wait_fixed(2), stop=tenacity.stop_after_attempt(3))
        def _get_project(name: str):
            project = get_project(name)
            return project
        project = _get_project(self.name)
        self._set_item('uid', project.uid)
        self._set_item('owner', project.owner)

    def delete(self) -> None:
        """
        Deletes this project
        """
        raise_on_error(self._client.delete(self.name))

    def update_permission(self, user: User, permissions: dict):
        """
        Updates the read/write access for a user on this project.

        Arguments:
            user: The user to update permissions for
            permissions: a dictionary of the read/write for the user

        Example:
        >>> p.update_permission(user, {'read': True, 'write': False})

        """
        for k, v in permissions.items():
            if k not in ['read', 'write']:
                raise ValueError("can only set read or write as permissions")
            if not isinstance(v, bool):
                raise ValueError("permissions must be boolean values for read/write")
        raise_on_error(self._client.put(f'{self.name}/permission/{user.subject}', **permissions))

    def permission(self, user: User):
        """
        Gets the read/write permissions of a user on this project

        Arguments:
            user: The user to check permissions for.
        """
        res = raise_on_error(self._client.get(f'{self.name}/permission/{user.subject}'))
        return res.json()

    @property
    def keywords(self):
        """
        Keywords related to this project
        """
        return list(map(str.strip, self['keywords'].split(',')))

    @keywords.setter
    def keywords(self, v: Union[list, str]):
        if isinstance(v, str):
            self._set_item('keywords', v)
            return
        elif not isinstance(v, (list, tuple)):
            raise ValueError("keywords must be a list of strings")

        self._set_item('keywords', ', '.join(v))


# Only one project can be active at one time. Certain functions (e.g. in Entanglement)
# will reference this project. This is the global project by default.
active_project = None


def set_active_project(p: Union[Project, str]) -> Project:
    """
    Sets the active project. Can either be a project name/uid or a Project
    """
    global active_project
    if isinstance(p, (Project, dict)):
        active_project = Project(**p)
    else:
        active_project = get_project(p)

    return active_project


def get_active_project() -> Project:
    """
    Gets the active project. If none exists, returns a handle to the
    'global' project.
    """
    global active_project
    if active_project is None:
        set_active_project('global')
    return active_project


class ProjectDescr(BaseDescr):
    """A geodesic Project/Entanglement Subgraph

    Returns a Project object, sets the project name on the base object

    """
    def _get(self, obj: object, objtype=None) -> dict:
        # Try to get the private attribute by name (e.g. '_project')
        project = getattr(obj, self.private_name, None)
        if project is not None:
            # Return it if it exists
            return project

        try:
            project_uid = self._get_object(obj)
            project = get_project(project_uid)
            setattr(obj, self.private_name, project)
        except KeyError:
            self._attribute_error(objtype)
        return project

    def _set(self, obj: object, value: object) -> None:
        # Reset the private attribute (e.g. "_project") to None
        setattr(obj, self.private_name, None)

        if isinstance(value, (Project, dict)):
            self._set_object(obj, Project(**value).uid)
        elif isinstance(value, str):
            self._set_object(obj, value)
        else:
            raise ValueError(f"invalid value type {type(value)}")

    def _validate(self, obj: object, value: object) -> None:
        if not isinstance(value, (Project, str, dict)):
            raise ValueError(f"'{self.public_name}' must be a Project or a string")

        # If the project was set, we need to validate that it exists and the user has access
        project_name = None
        if isinstance(value, str):
            project_name = value
        else:
            project_name = Project(**value).name

        try:
            get_project(project_name, refresh=True)
        except Exception as e:
            raise ValueError("project '{project_name}' does not exist or user doesn't have access") from e
