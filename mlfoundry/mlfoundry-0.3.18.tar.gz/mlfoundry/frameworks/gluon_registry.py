import mlflow

from mlfoundry.exceptions import MlFoundryException
from mlfoundry.frameworks.base_registry import BaseRegistry


class GluonRegistry(BaseRegistry):
    def log_model(self, model, artifact_path: str, **kwargs):
        """
        Log Gluon model
        Args:
            model : the model to be registered
            artifact_path (str): artifact_path
        """
        mlflow.gluon.log_model(model, artifact_path=artifact_path)

    def load_model(self, model_file_path: str, dest_path: str = None, **kwargs):
        """
        Load Gluon model
        """
        if "ctx" not in kwargs.keys():
            raise MlFoundryException("ctx is required")
        ctx = kwargs["ctx"]
        return mlflow.gluon.load_model(model_file_path, ctx, dest_path)
