import unittest
from unittest.mock import MagicMock

from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow


class TestAbstractAutoloadFlow(unittest.TestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.vendor_attr_name = "Test Vendor"
        self.model_attr_name = "Test Model"
        self.autoload_details = autoload_details = MagicMock(
            attributes=[
                MagicMock(
                    attribute_name="Shell Name.Vendor",
                    attribute_value=self.vendor_attr_name,
                    relative_address="",
                ),
                MagicMock(
                    attribute_name="Shell Name.Model",
                    attribute_value=self.model_attr_name,
                    relative_address="",
                ),
                MagicMock(
                    attribute_name="Shell Name.Some Attribute",
                    attribute_value="Some Attribute",
                    relative_address="",
                ),
            ]
        )

        class ImplementedTestAbstractAutoloadFlow(AbstractAutoloadFlow):
            def _autoload_flow(self, supported_os, resource_model):
                return autoload_details

        self.autoload_flow = ImplementedTestAbstractAutoloadFlow(logger=self.logger)

    def test_discover(self):
        supported_os = MagicMock()
        resource_model = MagicMock()
        self.autoload_flow._log_device_details = MagicMock()
        # act
        result = self.autoload_flow.discover(
            supported_os=supported_os, resource_model=resource_model
        )
        # verify
        self.assertEqual(result, self.autoload_details)
        self.autoload_flow._log_device_details.assert_called_once_with(
            self.autoload_details
        )

    def test_log_device_details(self):
        # act
        self.autoload_flow._log_device_details(details=self.autoload_details)
        # verify
        self.logger.info.assert_called_once_with(
            'Device Vendor: "{}", '
            'Model: "{}", '
            'OS Version: ""'.format(self.vendor_attr_name, self.model_attr_name)
        )
