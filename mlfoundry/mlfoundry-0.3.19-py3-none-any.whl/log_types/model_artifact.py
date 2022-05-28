from mlfoundry.enums import ModelFramework
from mlfoundry.log_types.pydantic_base import PydanticBase


class ModelArtifactRunLog(PydanticBase):
    artifact_path: str
    framework: ModelFramework

    @staticmethod
    def get_log_type() -> str:
        return "model"
