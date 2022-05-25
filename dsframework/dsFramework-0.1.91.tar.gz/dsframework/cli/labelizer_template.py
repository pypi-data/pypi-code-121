from dsframework.pipeline import LabelizerBase
from dsframework.config import ZIDSConfig
from dsframework.shared import SharedArtifacts


class generatedClass(LabelizerBase):
    def __init__(self, name: str = "generatedClassName", model_path: str = '', use_dummy_model=False,
                 threshold: float = 0.5, shared_artifacts: SharedArtifacts = None, config: ZIDSConfig = None, **kwargs):
        super(generatedClass, self).__init__(name=name, model_path=model_path, use_dummy_model=use_dummy_model,
                               threshold=threshold, shared_artifacts=shared_artifacts, config=config, **kwargs)

    def __call__(self, **kwargs) -> LabelizerBase:
        raise NotImplementedError

    def init_predictor(self, model_path: str = '', use_dummy_model=False, threshold: float = 0.5) -> None:
        """
        init predictor of model (Catboost model)
        :param model_path: path to model
        :param use_dummy_model: use dummy model or not
        :param threshold: threshold
        """
        raise NotImplementedError

    def init_forcer(self, config: ZIDSConfig, shared_objects: SharedArtifacts):
        """
        init forcer
        """
        raise NotImplementedError
