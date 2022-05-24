from typing import Dict, Any, Optional

from pydantic import BaseModel


class Node(BaseModel):
    id: Optional[str]
    label: Optional[str]
    properties: Optional[Dict[str, Any]]
