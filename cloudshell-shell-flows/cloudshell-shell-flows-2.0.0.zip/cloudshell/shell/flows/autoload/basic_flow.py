from abc import abstractmethod

from cloudshell.logging.utils.decorators import command_logging

from cloudshell.shell.flows.interfaces import AutoloadFlowInterface


class AbstractAutoloadFlow(AutoloadFlowInterface):
    def __init__(self, logger):
        """Autoload Flow.

        :param logging.Logger logger:
        """
        self._logger = logger

    @abstractmethod
    def _autoload_flow(self, supported_os, resource_model):
        """Build autoload details, has to be implemented.

        :param collections.Iterable supported_os:
        :param cloudshell.shell.standards.autoload_generic_models.GenericResourceModel resource_model:  # noqa: E501
        :rtype: cloudshell.shell.core.driver_context.AutoLoadDetails
        """
        pass

    def _log_device_details(self, details):
        needed_attrs = {"Vendor", "Model", "OS Version"}
        attrs = {}

        for attr in details.attributes:
            attr_name = attr.attribute_name.rsplit(".", 1)[-1]

            if attr.relative_address == "" and attr_name in needed_attrs:
                attrs[attr_name] = attr.attribute_value

                needed_attrs.remove(attr_name)
                if not needed_attrs:
                    break

        self._logger.info(
            'Device Vendor: "{}", Model: "{}", OS Version: "{}"'.format(
                attrs.get("Vendor", ""),
                attrs.get("Model", ""),
                attrs.get("OS Version", ""),
            )
        )

    @command_logging
    def discover(self, supported_os, resource_model):
        """Discover the resource.

        :param collections.Iterable supported_os:
        :param cloudshell.shell_standards.autoload_generic_models.GenericResourceModel resource_model:  # noqa: E501
        :return:
        """
        details = self._autoload_flow(supported_os, resource_model)

        self._log_device_details(details)
        return details
