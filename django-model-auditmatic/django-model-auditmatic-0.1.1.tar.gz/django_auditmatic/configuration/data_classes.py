"""
    configuration data classes
"""
from collections import defaultdict
from typing import Dict, List

from django.conf import settings


class AuditMaticAppConfiguration:
    def __init__(self):
        pass


class AuditMaticPermissionConfiguration:
    def __init__(self):
        pass


class AuditMaticConfiguration:
    def __init__(self):
        self.apps = {}
        self.permission = {}


class ConfiguredNames:
    """
    A data object to hold configured name values.
    """

    def __init__(
        self, app_names: List, model_names: Dict, model_m2m_names: Dict, allow_any: Dict
    ):
        self.app_names = app_names
        self.model_names = model_names
        self.allow_any = allow_any
        self.model_m2m_names = model_m2m_names

    @staticmethod
    def process_app_models(
        app_name, app_names, app_models, model_names, model_m2m_names, allow_any
    ):
        """
            process app configured models
        :param allow_any:
        :param app_name:
        :param app_names:
        :param app_models:
        :param model_names:
        :param model_m2m_names:
        :return:
        """
        lowered_app_name = app_name.lower()
        app_names.append(lowered_app_name)
        app_models_type = type(app_models)
        if app_models_type == set:
            names = [(name, {}) for name in app_models]
        elif app_models_type == dict:
            names = app_models.items()
        else:
            raise NotImplementedError()
        for model_name, model_configuration in names:
            lowered_model_name = model_name.lower()
            model_names[lowered_app_name].append(lowered_model_name)
            m2m_key = f"{lowered_app_name}_{lowered_model_name}"
            model_m2m_configured_names = model_configuration.get("m2m", [])

            # print("m2m names ", model_m2m_configured_names)
            if model_m2m_configured_names == any:  # pylint: disable=W0143
                # type(model_m2m_configured_names) == callable and \

                model_m2m_names[m2m_key].append(any)
                # print("is any")
            else:
                for value in model_m2m_configured_names:
                    model_m2m_names[m2m_key].append(value)

            model_allow = model_configuration.get("allow", False)
            if model_allow == any:
                allow_any[lowered_model_name] = True

    @staticmethod
    def from_settings():
        """
            creates ConfiguredNames from settings.
        :return:
        """
        configured_apps = settings.AUDITMATIC["apps"]

        app_names = []
        model_names = defaultdict(list)
        model_m2m_names = defaultdict(list)
        allow_any = defaultdict(bool)
        for app_name, app_models in configured_apps.items():
            ConfiguredNames.process_app_models(
                app_name, app_names, app_models, model_names, model_m2m_names, allow_any
            )

        return ConfiguredNames(app_names, model_names, model_m2m_names, allow_any)


class ModelNames:
    """
    a data object that stores info about a model
    """

    def __init__(self, app_name, model_name, model):
        self.app_name = app_name
        self.model_name = model_name
        self.model = model

    @staticmethod
    def from_model(model):
        """generates an object from a model"""
        app_and_model_name = str(model._meta)
        app_name, model_name = app_and_model_name.split(".")
        return ModelNames(app_name, model_name, model)

    def __repr__(self):
        return f"{self.app_name}_{self.model_name}"
