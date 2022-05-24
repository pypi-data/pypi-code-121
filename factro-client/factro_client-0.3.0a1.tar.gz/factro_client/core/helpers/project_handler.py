from typing import List, Optional
import logging


from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, Undefined

from .base_handler import BaseHandler

logger = logging.getLogger('factro_client')

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Project:
    id: str
    title: str
    number: int
    creator_id: str
    mandant_id: str
    is_archived: bool
    is_draft: bool
    project_state: str
    custom_fields: Optional[dict]
    description: Optional[str] = ''
    end_date: Optional[str] = ''
    start_date: Optional[str] = ''
    company_id: Optional[str] = ''
    company_contact_id: Optional[str] = ''
    officer_id: Optional[str] = ''
    planned_effort: Optional[float] = 0.0
    realized_effort: Optional[float] = 0.0
    remaining_effort: Optional[float] = 0.0
    priority: Optional[int] = 0

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class ProjectStructure:
    id: str
    type: str
    children: "List[Optional[ProjectStructure]]"


class ProjectHandler(BaseHandler):

    def __init__(self, url: str, api_key: str):
        super(ProjectHandler, self).__init__(url, api_key)

    def get_project_by_id(self, project_id) -> Project:
        path = f"/api/core/projects/{project_id}"

        json_data = self.do_get(path)

        logger.debug(f"ProjectHandler.get_project_by_id({project_id} -> {json_data}")

        project = Project.schema().load(json_data)

        return project

    def get_projects(self) -> List[Project]:
        path = f"/api/core/projects"
        json_data = self.do_get(path)

        projects = Project.schema().load(json_data, many=True)

        return projects

    def get_project_structure(self, project_id: str) -> ProjectStructure:
        path = f"/api/core/projects/{project_id}/structure"

        json_data = self.do_get(path)

        structure = ProjectStructure.schema().load(json_data)

        return structure
