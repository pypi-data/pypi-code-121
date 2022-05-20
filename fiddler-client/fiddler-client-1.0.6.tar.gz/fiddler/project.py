from typing import List, Optional

from fiddler.connection import Connection
from fiddler.dataset import Dataset
from fiddler.model import Model
from fiddler.utils.general_checks import type_enforce


class Project:
    def __init__(self, connection: Connection, project_id: str):
        self.connection = connection
        self.project_id = project_id

    def list_models(self) -> List[str]:
        """List the names of all models in a project.

        :returns: List of strings containing the ids of each model in the
            specified project.
        """
        project_id = type_enforce('project_id', self.project_id, str)
        path = ['list_models', self.connection.org_id, project_id]
        res = self.connection.call(path, is_get_request=True)
        return res

    def delete(self):
        """Permanently delete a project.
        :returns: Server response for deletion action.
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)
        path = ['delete_project', self.connection.org_id, project_id]
        result = self.connection.call(path)
        return result

    def share(
        self,
        role: str,
        user_name: Optional[str] = None,
        team_name: Optional[str] = None,
    ):
        """Share a project with other users and/or teams.

        :param role: one of ["READ", "WRITE", "OWNER"].
        :param user_name: (optional) username, typically an email address.
        :param team_name: (optional) name of the team.

        :returns: Server response for creation action.
        """
        if user_name is None and team_name is None:
            err = 'one of user_name, team_name must be provided'
            raise ValueError(err)

        if user_name is not None and team_name is not None:
            err = 'Only one of user_name or team_name must be provided'
            raise ValueError(err)

        if role not in ['READ', 'WRITE', 'OWNER']:
            err = 'role must be one of READ, WRITE, or OWNER'
            raise ValueError(err)

        payload = {
            'role': role,
            'user_name': user_name,
            'team_name': team_name,
        }

        path = ['apply_project_role', self.connection.org_id, self.project_id]
        return self.connection.call(path, json_payload=payload)

    def unshare(
        self,
        role: str,
        user_name: Optional[str] = None,
        team_name: Optional[str] = None,
    ):
        """un-Share a project with other users and/or teams.

        :param role: one of ["READ", "WRITE", "OWNER"].
        :param user_name: (optional) username, typically an email address.
        :param team_name: (optional) name of the team.

        :returns: Server response for creation action.
        """
        if user_name is None and team_name is None:
            err = 'one of user_name, team_name must be provided'
            raise ValueError(err)

        if user_name is not None and team_name is not None:
            err = 'Only one of user_name or team_name must be provided'
            raise ValueError(err)

        if role not in ['READ', 'WRITE', 'OWNER']:
            err = 'role must be one of READ, WRITE, or OWNER'
            raise ValueError(err)

        payload = {
            'role': role,
            'user_name': user_name,
            'team_name': team_name,
        }

        path = ['delete_project_role', self.connection.org_id, self.project_id]
        return self.connection.call(path, json_payload=payload)

    def list_roles(self):
        """List the users and teams with access to a given project.

        :returns: list of users and teams with access to a given project.
        """
        path = ['roles', self.connection.org_id, self.project_id]
        return self.connection.call(path, is_get_request=True)

    def list_datasets(self) -> List[str]:
        """List the ids of all datasets in the organization.

        :returns: List of strings containing the ids of each dataset.
        """
        # Type enforcement
        project_id = type_enforce('project_id', self.project_id, str)

        path = ['list_datasets', self.connection.org_id, project_id]
        res = self.connection.call(path, is_get_request=True)

        return res

    def model(self, model_id: str) -> Model:
        return Model(self.connection, self.project_id, model_id)

    def dataset(self, dataset_id: str) -> Dataset:
        return Dataset(self.connection, self.project_id, dataset_id)
