from typing import Dict, Any, Optional

from pydantic import BaseModel


class Node(BaseModel):
    id: Optional[str]
    label: str
    properties: Optional[Dict[str, Any]]
