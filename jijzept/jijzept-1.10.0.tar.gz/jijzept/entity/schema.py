from pydantic import BaseModel


class SolverType(BaseModel):
    queue_name: str
    solver: str
