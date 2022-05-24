from pydantic import BaseModel
from typing import Optional


class TargetApp(BaseModel):
    app: str
    version: Optional[str] = "_"
    branch: Optional[str] = "_"

    def to_slashed_string(self):
        return f"{self.app}/{self.version}/{self.branch}"

    def to_provider_string(self):
        return f"{self.app}/{self.version}"

    @staticmethod
    def from_unique_slashed_string(slashed_string: str):
        target = slashed_string.split("/")
        if len(target) == 3:
            return TargetApp(app=target[0], version=target[1], branch=target[2])
        elif len(target) == 2:
            return TargetApp(app=target[0], version=target[1], branch="*")
        elif len(target) == 1:
            return TargetApp(app=target[0], version="*", branch="*")


