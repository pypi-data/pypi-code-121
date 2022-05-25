# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import inspect
from typing import Any, List, Tuple, Union

from azureml.automl.core import _codegen_utilities

from .model_template import AbstractModelTemplate

try:
    from azureml.contrib.automl.dnn.forecasting.wrapper.forecast_wrapper import DNNForecastWrapper, DNNParams
except ImportError:
    # We shouldn't hit this unless the model being inspected isn't DNN, in which case it doesn't matter.
    pass


class SingleForecastDnnModelTemplate(AbstractModelTemplate):
    def __init__(self, model: "DNNForecastWrapper") -> None:
        # DNNForecastWrapper classes (ForecastTCN, Deep4Cast) take zero params in __init__;
        # they have to be set externally. Perform a sanity check to ensure this is the case.
        init_sig = inspect.signature(model.__class__.__init__)
        if len(init_sig.parameters) > 1:
            raise NotImplementedError(f"{model.__class__.__name__} is unsupported")
        self.model = model
        self.params = self.model.params._params

    def _get_model_code(self) -> List[str]:
        params = {"params": self.params, "required": self.model.__class__.required_params}
        return [
            f"algorithm = {self.model.__class__.__name__}()",
            f"algorithm.params = {_codegen_utilities.generate_repr_str(DNNParams, params=params)}",
        ]

    def _get_support_code(self) -> List[str]:
        return []

    def _get_imports(self) -> List[Tuple[str, str, Any]]:
        imports = [_codegen_utilities.get_import(self.model.__class__), _codegen_utilities.get_import(DNNParams)]
        if hasattr(self.model, "_get_imports"):
            imports.extend(self.model._get_imports())
        imports.extend(_codegen_utilities.get_recursive_imports(self.params))
        return imports


class NamedForecastDnnModelTemplate(SingleForecastDnnModelTemplate):
    def __init__(self, model: "DNNForecastWrapper", model_name: Union[str, int]) -> None:
        super().__init__(model)
        self.model_name = model_name
