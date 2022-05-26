import mlflow

from mlfoundry.frameworks.base_registry import BaseRegistry


class LightGBMRegistry(BaseRegistry):
    def log_model(self, model, artifact_path: str, **kwargs):
        """
        Log LightGBM model
        Args:
            model : the model to be registered
            artifact_path (str): artifact_path
        """
        mlflow.lightgbm.log_model(model, artifact_path=artifact_path)

    def load_model(self, model_file_path: str, dest_path: str = None, **kwargs):
        """
        Load LightGBM model
        """
        return mlflow.lightgbm.load_model(model_file_path, dest_path)
