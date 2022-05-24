import time

from .. import CoreService_pb2 as pb
from ..collections.feature_sets import FeatureSets
from ..utils import Utils
from .user import User


class Project:
    def __init__(self, stub, project):
        self._project = project
        self._stub = stub
        self.feature_sets = FeatureSets(stub, project)

    @property
    def name(self):
        return self._project.name

    @property
    def description(self):
        return self._project.description

    @description.setter
    def description(self, value):
        update_request = pb.ProjectStringFieldUpdateRequest()
        update_request.new_value = value
        update_request.project_id = self._project.id
        self._stub.UpdateProjectDescription(update_request)
        self._refresh()

    @property
    def secret(self):
        return self._project.secret

    @secret.setter
    def secret(self, value):
        update_request = pb.ProjectBooleanFieldUpdateRequest()
        update_request.new_value = value
        update_request.project_id = self._project.id
        self._stub.UpdateProjectSecret(update_request)
        self._refresh()

    @property
    def locked(self):
        return self._project.locked

    @locked.setter
    def locked(self, value):
        update_request = pb.ProjectBooleanFieldUpdateRequest()
        update_request.new_value = value
        update_request.project_id = self._project.id
        self._stub.UpdateProjectLocked(update_request)
        self._refresh()

    @property
    def owner(self):
        return User(self._project.owner)

    @owner.setter
    def owner(self, email):
        request = pb.GetUserByMailRequest()
        request.email = email
        response = self._stub.GetUserByMail(request)
        user = response.user
        update_request = pb.ProjectUserFieldUpdateRequest()
        update_request.new_value.CopyFrom(user)
        update_request.project_id = self._project.id
        self._stub.UpdateProjectOwner(update_request)
        self._refresh()

    @property
    def author(self):
        return User(self._project.author)

    @property
    def custom_data(self):
        return self._project.custom_data

    @custom_data.setter
    def custom_data(self, value):
        update_request = pb.ProjectCustomDataUpdateRequest()
        update_request.new_value.CopyFrom(value)
        update_request.project_id = self._project.id
        self._stub.UpdateProjectCustomData(update_request)
        self._refresh()

    def delete(self, wait_for_completion=False):
        request = pb.DeleteProjectRequest()
        request.project.CopyFrom(self._project)
        self._stub.DeleteProject(request)
        exists_request = pb.ProjectExistsRequest()
        exists_request.project_id = self._project.id
        if wait_for_completion:
            while self._stub.ProjectExists(exists_request).exists:
                time.sleep(1)
                print("Waiting for project '{}' deletion".format(self._project.name))

    def add_owners(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Owner)

    def add_editors(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Editor)

    def add_consumers(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Consumer)

    def remove_owners(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Owner)

    def remove_editors(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Editor)

    def remove_consumers(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Consumer)

    def _add_permissions(self, user_emails, permission):
        request = pb.ProjectPermissionRequest()
        request.project.CopyFrom(self._project)
        request.user_emails.extend(user_emails)
        request.permission = permission
        self._stub.AddProjectPermission(request)
        return self

    def _remove_permissions(self, user_emails, permission):
        request = pb.ProjectPermissionRequest()
        request.project.CopyFrom(self._project)
        request.user_emails.extend(user_emails)
        request.permission = permission
        self._stub.RemoveProjectPermission(request)
        return self

    def _refresh(self):
        request = pb.GetProjectRequest()
        request.project_name = self._project.name
        response = self._stub.GetProject(request)
        self._project = response.project

    def __repr__(self):
        return Utils.pretty_print_proto(self._project)
