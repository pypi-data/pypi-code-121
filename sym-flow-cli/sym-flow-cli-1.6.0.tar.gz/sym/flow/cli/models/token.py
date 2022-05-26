from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SymAccessToken(BaseModel):
    """Pydantic model for parsing Sym response after creating a Sym Token.
    The output should be a base64 encoded JWT
    """

    access_token: str


class SymTokenUser(BaseModel):
    """Pydantic model for parsing the simplified UserSchema outputted by GET /api/v1/tokens"""

    id: UUID
    type: str


class SymToken(BaseModel):
    """Pydantic model for parsing Sym response to GET /api/v1/tokens"""

    identifier: UUID
    user: SymTokenUser
    created_by: SymTokenUser
    expires_at: datetime
    updated_at: datetime
    label: Optional[str]
