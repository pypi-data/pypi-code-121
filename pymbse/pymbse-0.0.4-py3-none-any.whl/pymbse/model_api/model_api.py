from abc import ABC, abstractmethod

from pydantic import BaseModel

from pymbse.pymbse.config.pymbse_config import NotebookScriptConfig
from pymbse.pymbse.model_api.snapshot.model_snapshot import ModelSnapshot


class ModelAPI(BaseModel, ABC):
    root_model_config: NotebookScriptConfig
    ip_with_port: str
    root_model_metadata_hash: str
    input_parameters: dict

    def get_figures_of_merit(self) -> dict:
        return self.execute().figures_of_merit

    def get_artefacts(self) -> dict:
        return self.execute().artefacts

    def get_artefact(self, artefact_name: str) -> str:
        model_snapshot = self.execute()
        if artefact_name not in model_snapshot.artefacts:
            print('An artefact %s is missing. Returning an empty string.' % artefact_name)
            return ""

        return model_snapshot.artefacts[artefact_name]

    @abstractmethod
    def execute(self) -> ModelSnapshot:
        """Abstract method executing a model to be implemented by subclasses."""
