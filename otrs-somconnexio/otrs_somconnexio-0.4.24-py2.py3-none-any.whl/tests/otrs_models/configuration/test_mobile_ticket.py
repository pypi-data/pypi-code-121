# coding: utf-8
import unittest
from mock import Mock

from otrs_somconnexio.otrs_models.configurations.mobile_ticket import MobileTicketConfiguration


class MobileTicketConfigurationTestCase(unittest.TestCase):

    def test_init_with_injection(self):
        custom_mobile_config = Mock(spec=[
            'mobile_process_id',
            'mobile_activity_id',
            'mobile_ticket_type',
            'mobile_ticket_queue',
            'mobile_ticket_state',
            'mobile_ticket_priority'
        ])

        otrs_config = MobileTicketConfiguration(custom_mobile_config)

        self.assertEqual(
            otrs_config.process_id,
            custom_mobile_config.mobile_process_id
        )
        self.assertEqual(
            otrs_config.activity_id,
            custom_mobile_config.mobile_activity_id
        )
        self.assertEqual(
            otrs_config.type,
            custom_mobile_config.mobile_ticket_type
        )
        self.assertEqual(
            otrs_config.queue,
            custom_mobile_config.mobile_ticket_queue
        )
        self.assertEqual(
            otrs_config.state,
            custom_mobile_config.mobile_ticket_state
        )
        self.assertEqual(
            otrs_config.priority,
            custom_mobile_config.mobile_ticket_priority
        )
