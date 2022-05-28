import mlflow

from mlfoundry.frameworks.base_registry import BaseRegistry


class SpacyRegistry(BaseRegistry):
    def log_model(self, model, artifact_path: str, **kwargs):
        """
        Log Spacy model
        Args:
            model : the model to be registered
            artifact_path (str): artifact_path
        """
        mlflow.spacy.log_model(model, artifact_path=artifact_path)

    def load_model(self, model_file_path: str, dest_path: str = None, **kwargs):
        """
        Load Spacy model
        """
        return mlflow.spacy.load_model(model_file_path, dest_path)
