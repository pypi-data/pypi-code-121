from pydantic import BaseModel, Field

SERVICE_KEY_SEPARATOR = ":"
SYM_CLOUD_KEY = "sym:cloud"


class BaseService(BaseModel):
    service_type: str = Field(alias="slug")
    external_id: str

    @property
    def service_key(self):
        return SERVICE_KEY_SEPARATOR.join([self.service_type, self.external_id])


class Service(BaseService):
    id: str
    label: str
