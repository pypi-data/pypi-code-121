from typing import Optional, Dict, Any

from pydantic import BaseModel


class Relationship(BaseModel):
    id: Optional[str]
    relationship_name: str
    properties: Optional[Dict[str, Any]]
