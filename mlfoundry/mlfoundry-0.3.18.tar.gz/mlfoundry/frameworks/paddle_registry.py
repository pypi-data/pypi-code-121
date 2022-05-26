import mlflow

from mlfoundry.frameworks.base_registry import BaseRegistry


class PaddleRegistry(BaseRegistry):
    def log_model(self, model, artifact_path: str, **kwargs):
        """
        Log Paddle model
        Args:
            model : the model to be registered
            artifact_path (str): artifact_path
        """
        mlflow.paddle.log_model(model, artifact_path=artifact_path)

    def load_model(self, model_file_path: str, dest_path: str = None, **kwargs):
        """
        Load Paddle model
        """
        model = kwargs.get("model")
        return mlflow.paddle.load_model(self.model_uri, model=model, dst_path=dest_path)
