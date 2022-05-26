from pydantic import BaseModel


class TenantInfo(BaseModel):
    tenant_id: str
    auth_server_url: str

    class Config:
        allow_mutation = False
