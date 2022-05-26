import logging

from humps.main import decamelize

from nwon_django_toolbox.settings import NWON_DJANGO_SETTINGS

LOGGER = logging.getLogger(NWON_DJANGO_SETTINGS.logger_name)


def check_object_against_parameter(object_to_test: dict, parameter: dict):
    for key in parameter:

        """
        Skip parameters. This might make sense for paramters that do not get
        returned like some of the polymorphic models
        """
        if key in NWON_DJANGO_SETTINGS.keys_to_skip_on_api_test:
            continue

        if key in key and isinstance(object_to_test[key], dict):
            parameter_value = decamelize(object_to_test[key]).__str__()
        else:
            parameter_value = parameter[key].__str__()

        if key in parameter and isinstance(parameter[key], dict):
            target_value = decamelize(object_to_test[key]).__str__()
        else:
            target_value = object_to_test[key].__str__()

        if target_value != parameter_value:
            LOGGER.debug(
                "Key "
                + key
                + " differs, \nParameter: \n"
                + parameter_value
                + " \n\nObject to test: \n"
                + target_value
            )

        assert parameter_value == target_value
