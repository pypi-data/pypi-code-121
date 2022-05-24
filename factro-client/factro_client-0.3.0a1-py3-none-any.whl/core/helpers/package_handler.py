from ctypes import Structure
from importlib.resources import Package
from typing import List, Optional

from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, Undefined

from .base_handler import BaseHandler

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Package:
    id: str
    mandant_id: str
    title: str
    number: int
    change_date: str
    creator_id: str
    custom_fields: Optional[dict]
    description: Optional[str] = ''
    end_date: Optional[str] = ''
    start_date: Optional[str] = ''
    company_id: Optional[str] = ''
    company_contact_id: Optional[str] = ''
    officer_id: Optional[str] = ''
    parent_package_id: Optional[str] = ''
    planned_effort: Optional[float] = 0.0
    project_id: Optional[str] = ''
    realized_effort: Optional[float] = 0.0
    remaining_effort: Optional[float] = 0.0


class PackageHandler(BaseHandler):

    def __init__(self, url: str, api_key: str):
        super(PackageHandler, self).__init__(url, api_key)

    def get_packages_by_project_id(self, project_id) -> List[Package]:
        path = f"/api/core/projects/{project_id}/packages"

        json_data = self.do_get(path)

        packages = Package.schema().load(json_data, many=True)

        return packages

    def get_package_by_id(self, package_id) -> Package:
        path = f"/api/core/packages/{package_id}"

        json_data = self.do_get(path)

        package = Package.schema().load(json_data)

        return package
