from mlfoundry.enums import ModelFramework
from mlfoundry.exceptions import MlFoundryException
from mlfoundry.frameworks.base_registry import BaseRegistry
from mlfoundry.frameworks.fastai_registry import FastAIRegistry
from mlfoundry.frameworks.gluon_registry import GluonRegistry
from mlfoundry.frameworks.h2o_registry import H2ORegistry
from mlfoundry.frameworks.keras_registry import KerasRegistry
from mlfoundry.frameworks.lightgbm_registry import LightGBMRegistry
from mlfoundry.frameworks.onnx_registry import ONNXRegistry
from mlfoundry.frameworks.paddle_registry import PaddleRegistry
from mlfoundry.frameworks.pytorch_registry import PyTorchRegistry
from mlfoundry.frameworks.sklearn_registry import SkLearnRegistry
from mlfoundry.frameworks.spacy_registry import SpacyRegistry
from mlfoundry.frameworks.statsmodel_registry import StatsModelsRegistry
from mlfoundry.frameworks.tensorflow_registry import TensorflowRegistry
from mlfoundry.frameworks.xgboost_registry import XGBoostRegistry

MODEL_FRAMEWORK_TO_REGISTRY = {
    ModelFramework.SKLEARN: SkLearnRegistry,
    ModelFramework.TENSORFLOW: TensorflowRegistry,
    ModelFramework.PYTORCH: PyTorchRegistry,
    ModelFramework.KERAS: KerasRegistry,
    ModelFramework.XGBOOST: XGBoostRegistry,
    ModelFramework.LIGHTGBM: LightGBMRegistry,
    ModelFramework.FASTAI: FastAIRegistry,
    ModelFramework.H2O: H2ORegistry,
    ModelFramework.ONNX: ONNXRegistry,
    ModelFramework.SPACY: SpacyRegistry,
    ModelFramework.STATSMODELS: StatsModelsRegistry,
    ModelFramework.GLUON: GluonRegistry,
    ModelFramework.PADDLE: PaddleRegistry,
}


def get_model_registry(
    model_framework: ModelFramework, *args, **kwargs
) -> BaseRegistry:
    if model_framework not in MODEL_FRAMEWORK_TO_REGISTRY:
        raise MlFoundryException(f"{model_framework} is not registerd")
    return MODEL_FRAMEWORK_TO_REGISTRY[model_framework](*args, **kwargs)
