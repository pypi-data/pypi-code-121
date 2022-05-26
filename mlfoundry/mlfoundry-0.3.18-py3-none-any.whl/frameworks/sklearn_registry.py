import mlflow

from mlfoundry.frameworks.base_registry import BaseRegistry


class SkLearnRegistry(BaseRegistry):
    def log_model(self, model, artifact_path: str, **kwargs):
        """
        Log SkLearn model
        Args:
            model : the model to be registered
            artifact_path (str): artifact_path
        """
        mlflow.sklearn.log_model(model, artifact_path=artifact_path)

    def load_model(self, model_file_path: str, dest_path: str = None, **kwargs):
        """
        Load SkLearn model
        """
        return mlflow.sklearn.load_model(model_file_path, dest_path)
