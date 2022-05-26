import mlflow

from mlfoundry.frameworks.base_registry import BaseRegistry


class H2ORegistry(BaseRegistry):
    def log_model(self, model, artifact_path: str, **kwargs):
        """
        Log H2O model
        Args:
            model : the model to be registered
            artifact_path (str): artifact_path
        """
        mlflow.h2o.log_model(model, artifact_path=artifact_path)

    def load_model(self, model_file_path: str, dest_path: str = None, **kwargs):
        """
        Load H2O model
        """
        return mlflow.h2o.load_model(model_file_path, dest_path)
