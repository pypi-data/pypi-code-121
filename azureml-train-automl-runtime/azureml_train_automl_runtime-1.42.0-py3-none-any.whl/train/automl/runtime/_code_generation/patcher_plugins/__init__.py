# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from contextlib import ExitStack, contextmanager
from typing import Any, Callable, ContextManager, Dict, Iterable, cast

from azureml.automl.core import _codegen_utilities

from .abstract_code_generator import AbstractCodeGenerator
from .base_estimator import BaseEstimatorCodeGenerator
from .count_vectorizer import CountVectorizerCodeGenerator
from .cross_validation_target_encoder import CrossValidationTargetEncoderCodeGenerator
from .enum import EnumCodeGenerator
from .featurization_config import FeaturizationConfigCodeGenerator
from .model_based_target_encoder import ModelBasedTargetEncoderCodeGenerator
from .multi_grain_forecast_base import MultiGrainForecastBaseCodeGenerator
from .passthrough import PassthroughCodeGenerator
from .quantile_loss import QuantileLossCodeGenerator
from .rolling_window import RollingWindowCodeGenerator

plugins = [
    PassthroughCodeGenerator(),
    RollingWindowCodeGenerator(),
    MultiGrainForecastBaseCodeGenerator(),
    FeaturizationConfigCodeGenerator(),
    CountVectorizerCodeGenerator(),
    CrossValidationTargetEncoderCodeGenerator(),
    ModelBasedTargetEncoderCodeGenerator(),
    QuantileLossCodeGenerator(),
    BaseEstimatorCodeGenerator(),
    EnumCodeGenerator(),
]


class CompositeCodeGenerator(AbstractCodeGenerator):
    def patch(self) -> Any:
        return self.patch_with_settings(_codegen_utilities.OUTPUT_SINGLE_LINE, _codegen_utilities.REWRITE_NAMESPACE)

    @contextmanager
    def patch_with_settings(self, single_line_output: bool, rewrite_namespaces: bool) -> Any:
        old_state = _codegen_utilities.OUTPUT_SINGLE_LINE, _codegen_utilities.REWRITE_NAMESPACE
        try:
            _codegen_utilities.OUTPUT_SINGLE_LINE = single_line_output
            _codegen_utilities.REWRITE_NAMESPACE = rewrite_namespaces
            with ExitStack() as stack:
                for plugin in plugins:
                    stack.enter_context(cast(ContextManager[Callable[..., str]], plugin.patch()))
                yield
        finally:
            _codegen_utilities.OUTPUT_SINGLE_LINE, _codegen_utilities.REWRITE_NAMESPACE = old_state

    @classmethod
    def can_handle(cls, obj: Any) -> bool:
        return any(plugin.can_handle(obj) for plugin in plugins)

    @classmethod
    def get_repr(cls, obj: Any) -> str:
        for plugin in plugins:
            if plugin.can_handle(obj):
                return plugin.get_repr(obj)
        raise ValueError()

    @classmethod
    def get_params(cls, obj: Any) -> Dict[str, Any]:
        for plugin in plugins:
            if plugin.can_handle(obj):
                return plugin.get_params(obj)
        raise ValueError()

    @classmethod
    def get_imports(cls, obj: Any) -> Iterable[_codegen_utilities.ImportInfoType]:
        for plugin in plugins:
            if plugin.can_handle(obj):
                return plugin.get_imports(obj)
        raise ValueError()


patcher = CompositeCodeGenerator()
