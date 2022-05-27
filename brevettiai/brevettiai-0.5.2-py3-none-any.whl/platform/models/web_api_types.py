from pydantic import Field, PrivateAttr
from typing import Optional, List, Dict, Union

from brevettiai.platform.models import Dataset, CamelModel


class ReportType(CamelModel):
    id: str
    created: str
    name: str
    status: int
    version: Optional[str]
    short_description: Optional[str]
    long_description: Optional[str]
    settings_schema_name: Optional[str]
    settings_schema_path: Optional[str]
    can_run_on_projects: bool
    can_run_on_applications: bool
    can_run_on_models: bool
    docker_image: Optional[str]
    max_runtime_in_seconds: int
    instance_count: int
    instance_type: Optional[str]
    volume_size_in_gb: int = Field(alias="volumeSizeInGB")
    duplicate_of: Optional[str]
    model_type_ids: List[str]
    model_types: Optional[str]
    organization_id: Optional[str]
    organization: Optional[str]


class ModelType(CamelModel):
    id: str
    created: str = Field(default="")
    name: str
    status: int = Field(default=-1)
    version: Optional[str]
    short_description: Optional[str]
    long_description: Optional[str]
    settings_schema_name: Optional[str]
    settings_schema_path: Optional[str]
    docker_image: Optional[str]
    max_runtime_in_seconds: int = Field(default=-1)
    instance_count: int = Field(default=1)
    instance_type: Optional[str]
    volume_size_in_gb: int = Field(default=-1, alias="volumeSizeInGB")
    duplicate_of: Optional[str]
    report_type_ids: List[str] = Field(default_factory=list)
    report_types: Optional[str]
    organization_id: Optional[str]
    organization: Optional[str]


class Model(CamelModel):
    id: str
    api_key: str
    created: str
    started: Optional[str]
    completed: Optional[str]
    job_id: Optional[str]
    has_deployments: Optional[str]
    name: str
    dataset_ids: Optional[List[str]] = Field(alias="datasets")  # deprecated?
    model_type_id: Optional[str]
    model_type_status: int
    model_url: Optional[str]
    version: Optional[str]
    report_type_ids: Optional[List[str]]
    settings: str
    tag_ids: Optional[List[str]] = Field(default_factory=list)
    application_id: Optional[str]

    _datasets: List[Dataset] = PrivateAttr(None)

    @property
    def has_api_key(self):
        return self.api_key != '<NO_API_KEY>'

    def get_datasets(self, api):
        if self._datasets is None:
            self._datasets = [api.get_dataset(x) for x in self.dataset_ids]
        return self._datasets


class Report(CamelModel):
    id: str
    api_key: str
    created: str
    started: Optional[str]
    completed: Optional[str]
    job_id: Optional[str]
    has_deployments: Optional[str]
    name: str
    dataset_ids: Optional[List[str]]
    model_ids: Optional[List[str]] = Field(alias="models")
    parent_id: str
    parent_name: Optional[str]
    parent_type: str
    parent_version: Optional[str]
    project_id: Optional[str]

    report_type_id: str
    report_type_name: Optional[str]
    report_type_status: int = -1
    report_type_version: Optional[str]
    settings: str
    tag_ids: Optional[List[str]]
    config_url: Optional[str]

    _datasets: List[Dataset] = PrivateAttr(None)

    @property
    def has_api_key(self):
        return self.api_key != '<NO_API_KEY>'

    def get_datasets(self, api):
        if self._datasets is None:
            self._datasets = [api.get_dataset(x) for x in self.dataset_ids]
        return self._datasets


class Application(CamelModel):
    id: str
    created: str
    name: str
    description: Optional[str]
    type: int = Field(default=1, ge=0, le=1)
    thumbnail_data: Optional[str] = Field(alias="thumbnail")
    training_dataset_ids: List[str] = Field(default_factory=list)
    test_dataset_ids: List[str] = Field(default_factory=list)
    model_ids: List[str] = Field(default_factory=list)
    starred_model_ids: List[str] = Field(default_factory=list)

    classes: Optional[List[str]] = Field(default_factory=list)
    class_map: Optional[Dict[str, Union[str, List[str]]]] = Field(default_factory=dict)

    @property
    def related_ids(self):
        return {self.id, *self.model_ids, *self.starred_model_ids, *self.training_dataset_ids, *self.test_dataset_ids}


class Project(CamelModel):
    id: str
    created: str
    name: str
    description: Optional[str]
    thumbnail_data: Optional[str] = Field(alias="thumbnail")
    applications: List[Application] = Field(default_factory=list)


class Device(CamelModel):
    id: str
    created: str
    name: str
    password: Optional[str]
    actual_configuration: Optional[str]
    desired_configuration: Optional[str]
    firmware_version: str
    datasets: Optional[List[Dataset]] = Field(default_factory=list)
    deployments: Optional[List[dict]] = Field(default_factory=list)
    tag_ids: List[str] = Field(default_factory=list)
    applications: List[Application] = Field(default_factory=list)


class Permission(CamelModel):
    id: str
    granted: str
    role: str
    by_group: bool


class UserPermissions(CamelModel):
    datasets: List[Permission]
    models: List[Permission]
    devices: List[Permission]
    projects: List[Permission]


class User(CamelModel):
    id: str
    first_name: str
    last_name: str
    username: str
    accepts_transactional_emails: bool
    is_email_confirmed: bool
    has_password: bool
    email: str
    phone_number: Optional[str]
    status_message: Optional[str]
    is_admin: bool
    is_admin_or_power_user: bool
    has_access_to_master_mode: bool
    api_key: str
    permissions: UserPermissions
    plan: int
    must_authenticate_externally: bool


class SftpUser(CamelModel):
    user_name: str
    folder: Optional[str]
    private_key: Optional[str]
    public_key: Optional[str]


class FileEntry(CamelModel):
    last_modified: Optional[str]
    link: Optional[str]
    mime_type: str
    name: str
    size: Optional[int]
    is_prefix: bool
    tile_source: Optional[str]
