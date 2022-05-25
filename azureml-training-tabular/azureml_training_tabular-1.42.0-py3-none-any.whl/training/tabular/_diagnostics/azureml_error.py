# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Type

# noinspection PyUnresolvedReferences
from azureml._common._error_definition.azureml_error import AzureMLError as _AzureMLError
from azureml._common._error_definition.error_definition import ErrorDefinition
# noinspection PyUnresolvedReferences
from azureml._common.exceptions import AzureMLException


class AzureMLError:

    @staticmethod
    def create(cls: "Type[ErrorDefinition]", **kwargs) -> AzureMLException:
        return AzureMLException._with_error(_AzureMLError.create(cls, **kwargs))
