import mlflow

from mlfoundry.frameworks.base_registry import BaseRegistry


class StatsModelsRegistry(BaseRegistry):
    def log_model(self, model, artifact_path: str, **kwargs):
        """
        Log StatsModels model
        Args:
            model : the model to be registered
            artifact_path (str): artifact_path
        """
        mlflow.statsmodels.log_model(model, artifact_path=artifact_path)

    def load_model(self, model_file_path: str, dest_path: str = None, **kwargs):
        """
        Load StatsModels model
        """
        return mlflow.statsmodels.load_model(model_file_path, dest_path)
