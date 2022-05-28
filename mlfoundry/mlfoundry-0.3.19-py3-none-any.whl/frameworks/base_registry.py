class BaseRegistry:
    def log_model(self, model, artifact_path: str, **kwargs):
        return NotImplementedError

    def load_model(self, model_file_path: str, **kwargs):
        return NotImplementedError
