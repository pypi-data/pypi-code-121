from mlfoundry.enums import FileFormat
from mlfoundry.log_types.pydantic_base import PydanticBase


class DatasetArtifact(PydanticBase):
    artifact_path: str

    @staticmethod
    def get_log_type() -> str:
        return "dataset"


class DatasetArtifactFeatures(PydanticBase):
    artifact_path: str
    format: FileFormat

    @staticmethod
    def get_log_type() -> str:
        return "dataset/features"


class DatasetArtifactActuals(PydanticBase):
    artifact_path: str
    format: FileFormat

    @staticmethod
    def get_log_type() -> str:
        return "dataset/actuals"


class DatasetArtifactPredictions(PydanticBase):
    artifact_path: str
    format: FileFormat

    @staticmethod
    def get_log_type() -> str:
        return "dataset/predictions"


class DatasetArtifactFeaturesProfile(PydanticBase):
    artifact_path: str

    @staticmethod
    def get_log_type() -> str:
        return "dataset/features/profile"


class DatasetArtifactActualsProfile(PydanticBase):
    artifact_path: str

    @staticmethod
    def get_log_type() -> str:
        return "dataset/actuals/profile"


class DatasetArtifactPredictionsProfile(PydanticBase):
    artifact_path: str

    @staticmethod
    def get_log_type() -> str:
        return "dataset/predictions/profile"
