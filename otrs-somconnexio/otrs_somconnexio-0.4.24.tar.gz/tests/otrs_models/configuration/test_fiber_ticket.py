# coding: utf-8
import unittest
from mock import Mock

from otrs_somconnexio.otrs_models.configurations.fiber_ticket import FiberTicketConfiguration


class FiberTicketConfigurationTestCase(unittest.TestCase):

    def test_init_with_injection(self):
        custom_fiber_config = Mock(spec=[
            'fiber_process_id',
            'fiber_activity_id',
            'fiber_ticket_type',
            'fiber_ticket_queue',
            'fiber_ticket_state',
            'fiber_ticket_proprity'
        ])

        otrs_config = FiberTicketConfiguration(custom_fiber_config)

        self.assertEqual(
            otrs_config.process_id,
            custom_fiber_config.fiber_process_id
        )
        self.assertEqual(
            otrs_config.activity_id,
            custom_fiber_config.fiber_activity_id
        )
        self.assertEqual(
            otrs_config.type,
            custom_fiber_config.fiber_ticket_type
        )
        self.assertEqual(
            otrs_config.queue,
            custom_fiber_config.fiber_ticket_queue
        )
        self.assertEqual(
            otrs_config.state,
            custom_fiber_config.fiber_ticket_state
        )
        self.assertEqual(
            otrs_config.priority,
            custom_fiber_config.fiber_ticket_proprity
        )
