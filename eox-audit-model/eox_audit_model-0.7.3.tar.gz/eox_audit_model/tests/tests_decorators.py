"""This file contains all the test for the decorators file.

Classes:
    TestAuditMethod: Test audit_method function..
"""
from django.test import TestCase
from mock import patch

from eox_audit_model.decorators import audit_method
from eox_audit_model.models import AuditModel


class TestAuditMethod(TestCase):
    """Test cases for the audit_method decorator."""

    @patch.object(AuditModel, 'execute_action')
    def test_decorator(self, execute_action_mock):
        """Test that decorator returns the value returned by execute_action.

        Expected behavior:
            - execute_action is called.
            - Return expected value.
        """
        @audit_method(action='TestAction')
        def test_method():
            """Do nothing"""

        # The method does not return anything.
        # however due to the decorator the value will be returned by execute_action
        result = test_method()  # pylint: disable=assignment-from-no-return

        execute_action_mock.assert_called_once()
        self.assertEqual(
            execute_action_mock(),
            result,
        )
