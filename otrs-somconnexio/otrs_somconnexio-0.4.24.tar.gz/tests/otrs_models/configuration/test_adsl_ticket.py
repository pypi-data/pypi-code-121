# coding: utf-8
import unittest
from mock import Mock

from otrs_somconnexio.otrs_models.configurations.adsl_ticket import ADSLTicketConfiguration


class ADSLTicketConfigurationTestCase(unittest.TestCase):

    def test_init_with_injection(self):
        custom_adsl_config = Mock(spec=[
            'adsl_process_id',
            'adsl_activity_id',
            'adsl_ticket_type',
            'adsl_ticket_queue',
            'adsl_ticket_state',
            'adsl_ticket_proprity'
        ])

        otrs_config = ADSLTicketConfiguration(custom_adsl_config)

        self.assertEqual(
            otrs_config.process_id,
            custom_adsl_config.adsl_process_id
        )
        self.assertEqual(
            otrs_config.activity_id,
            custom_adsl_config.adsl_activity_id
        )
        self.assertEqual(
            otrs_config.type,
            custom_adsl_config.adsl_ticket_type
        )
        self.assertEqual(
            otrs_config.queue,
            custom_adsl_config.adsl_ticket_queue
        )
        self.assertEqual(
            otrs_config.state,
            custom_adsl_config.adsl_ticket_state
        )
        self.assertEqual(
            otrs_config.priority,
            custom_adsl_config.adsl_ticket_proprity
        )
