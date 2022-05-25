# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Dict
from abc import ABC
from azureml.automl.core.shared.exceptions import ConfigException
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import DNNNotSupportedForManyModel
from azureml.automl.core.shared.reference_codes import ReferenceCodes


logger = logging.getLogger(__name__)


class TrainPipelineParameters(ABC):

    _MIN_TIMEOUT_DIFF = 300

    def __init__(self, automl_settings: Dict[str, Any]):
        self.automl_settings = automl_settings

    def validate(self, run_invocation_timeout):
        if self.automl_settings.get("enable_dnn", False):
            raise ConfigException._with_error(
                AzureMLError.create(
                    DNNNotSupportedForManyModel,
                    reference_code=ReferenceCodes._VALIDATE_DNN_ENABLED_MANY_MODELS))
        if "experiment_timeout_hours" not in self.automl_settings:
            self.automl_settings["experiment_timeout_hours"] = round((
                run_invocation_timeout - self._MIN_TIMEOUT_DIFF) / 3600, 2)
            message = "As the experiment_timeout_hours must be smaller than run_invocation_timeout - "\
                      "{}, we have set the value to {} automatically as we didn't find it in the settings.".\
                      format(self._MIN_TIMEOUT_DIFF, self.automl_settings["experiment_timeout_hours"])
            logger.warning(message)


class InferencePipelineParameters(ABC):
    def __init__(self):
        pass

    def validate(self):
        pass
