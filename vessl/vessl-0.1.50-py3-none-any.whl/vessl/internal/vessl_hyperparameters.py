import inspect

from urllib3.exceptions import MaxRetryError

from openapi_client import (
    ExperimentUpdateHyperparametersAPIInput,
    ResponseExperimentInfo,
)
from vessl.util import logger
from vessl.util.api import VesslApi
from vessl.util.exception import VesslApiException


class HyperparametersController(object):
    def __init__(self, api: VesslApi, experiment: ResponseExperimentInfo):
        object.__setattr__(self, "hyperparameters", Hyperparameters())
        object.__setattr__(self, "_api", api)
        object.__setattr__(self, "_experiment", experiment)

    def __setattr__(self, key, value):
        self.hyperparameters.__setattr__(key, value)

    def configure(self, api, experiment):
        object.__setattr__(self, "_api", api)
        object.__setattr__(self, "_experiment", experiment)

    def update_items(self, d=None):
        self.hyperparameters.update_items(d)

    def as_list_of_dict(self):
        return self.hyperparameters.as_list_of_dict()

    def update(self, d=None):
        self.hyperparameters.update_items(d)
        logger.debug(f"Update hyperparameters: {self.hyperparameters.as_list_of_dict()}")
        try:
            self._api.experiment_update_hyperparameters_api(
                organization_name=self._experiment.organization.name,
                project_name=self._experiment.project.name,
                experiment_number=self._experiment.number,
                experiment_update_hyperparameters_api_input=ExperimentUpdateHyperparametersAPIInput(
                    hyperparameters=self.hyperparameters.as_list_of_dict(),
                ),
            )

        except (MaxRetryError, VesslApiException) as e:
            logger.exception(
                "Failed to update hyperparameters to experiment", exc_info=e
            )

        except Exception as e:
            logger.exception("Unexpected error", exc_info=e)


class Hyperparameters(object):
    def __init__(self):
        object.__setattr__(self, "_items", dict())

    def __repr__(self):
        return str(dict(self._items))

    def __setattr__(self, key, value):
        key, value = self._validate(key, value)
        self._items[key] = value

    def __getattr__(self, key):
        return self._items[key]

    def __contains__(self, key):
        return key in self._items

    def keys(self):
        return [k for k in self._items.keys()]

    def as_list_of_dict(self):
        return [{"key": k, "value": v} for k, v in self._items.items()]

    def items(self):
        return [(k, v) for k, v in self._items.items()]

    def update_items(self, d=None):
        if d is None:
            return
        if isinstance(d, dict):
            d = self._validate_dict(d)
            self._items.update(d)
        elif inspect.getmodule(d).__name__ == "argparse":
            d = vars(d)
            d = self._validate_dict(d)
            self._items.update(d)

    def _validate_dict(self, d):
        validated_d = {}
        for k, v in d.items():
            k, v = self._validate(k, v)
            validated_d[k] = v
        return validated_d

    def _validate(self, key, value):
        key = key.strip()
        value = str(value)
        return key, value
