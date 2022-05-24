from typing import Dict, List, Optional
from pydantic import BaseModel


class KeycloakUser(BaseModel):
    name: str
    preferred_username: str
    given_name: str
    family_name: str
    email: str


class Roles(BaseModel):
    roles: List


class TokenInfo(KeycloakUser):
    realm_access: Optional[Roles]
    resource_access: Optional[Dict[str, Roles]]