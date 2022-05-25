from pydantic import BaseModel


class Snapshot(BaseModel):
    timestamp: str
    fqtn: str
