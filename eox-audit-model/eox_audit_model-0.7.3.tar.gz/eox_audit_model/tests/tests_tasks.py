"""This file contains all the test for the tasks file.

Classes:
    TestCreateAuditRegister: Test AuditModel.
"""
import logging
import traceback

from django.test import TestCase

from eox_audit_model.constants import Status
from eox_audit_model.models import AuditModel
from eox_audit_model.tasks import create_audit_register

LOG = logging.getLogger(__name__)


class TestAuditModel(TestCase):
    """Test cases for the model AuditModel."""

    def setUp(self):
        """Setup common conditions for every test case"""
        def valid_method(a, b, c, d):
            """Execute a mathematic operation."""
            LOG.info('This is an info message')
            return (a + b + c) / d

        self.valid_method = valid_method

    def test_create_record(self):
        """Test creation task functionality.

        Expected behavior:
            - There is a record in the data base with the right action.
        """
        action = 'Test action.'
        method = self.valid_method
        parameters = {
            'args': (1, 2),
            'kwargs': {'c': 3, 'd': 1},
        }

        create_audit_register(
            action=action,
            status=Status.SUCCESS,
            method_name=method.__name__,
            captured_logs='fake-logs',
            traceback_log=traceback.format_exc(),
            input_parameters=parameters,
            output_parameters=str(method(1, 2, 3, 1)),
            notes=None,
        )

        audit_register = AuditModel.objects.get(status=Status.SUCCESS)
        self.assertEqual(action, audit_register.action)

    def test_create_record_with_notes(self):
        """Test task notes creation functionality.

        Expected behavior:
            - The AuditNote register is created.
        """
        action = 'Test action.'
        method = self.valid_method
        parameters = {
            'args': (1, 2),
            'kwargs': {'c': 3, 'd': 1},
        }
        notes = [
            {
                'title': 'AuditNote',
                'description': 'this description is store in the audit note model.',
            },
        ]

        create_audit_register(
            action=action,
            status=Status.SUCCESS,
            method_name=method.__name__,
            captured_logs='fake-logs',
            traceback_log=traceback.format_exc(),
            input_parameters=parameters,
            output_parameters=str(method(1, 2, 3, 1)),
            notes=notes,
        )

        audit_register = AuditModel.objects.get(status=Status.SUCCESS)
        note = audit_register.auditnote_set.all()[0]
        self.assertEqual(notes[0]['title'], note.title)
