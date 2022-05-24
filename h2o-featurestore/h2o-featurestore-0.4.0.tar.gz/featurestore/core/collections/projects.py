from typing import List

from google.protobuf.empty_pb2 import Empty

from .. import CoreService_pb2 as pb
from ..entities.project import Project


class Projects:
    def __init__(self, stub):
        self._stub = stub
        self._default_lock_value = None

    def list(self) -> List[Project]:
        request = Empty()
        response = self._stub.ListProjects(request)
        return [Project(self._stub, p) for p in response.projects]

    def create(
        self,
        project_name: str,
        description: str = "",
        secret: bool = False,
        locked: bool = None,
    ) -> Project:

        if locked is None and self._default_lock_value is None:
            self._default_lock_value = self._stub.GetProjectsDefault(Empty()).locked
        if locked is None:
            locked_value = self._default_lock_value
        else:
            locked_value = locked
        request = pb.CreateProjectRequest()
        request.secret = secret
        request.project_name = project_name
        request.description = description
        request.locked = locked_value
        response = self._stub.CreateProject(request)
        if response.already_exists:
            print("Project '" + project_name + "' already exists.")
        return Project(self._stub, response.project)

    def get(self, project_name: str) -> Project:
        request = pb.GetProjectRequest()
        request.project_name = project_name
        response = self._stub.GetProject(request)
        return Project(self._stub, response.project)

    def __repr__(self):
        return "This class wraps together methods working with projects"
