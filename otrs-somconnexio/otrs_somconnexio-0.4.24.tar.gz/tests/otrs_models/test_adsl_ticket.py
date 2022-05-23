# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.adsl_ticket import ADSLTicket
from otrs_somconnexio.otrs_models.configurations.adsl_ticket import ADSLTicketConfiguration


class ADSLTicketTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.otrs_models.provision_ticket.Ticket')
    def test_build_ticket(self, MockTicket):
        customer_data = Mock(spec=['id'])
        service_data = Mock(spec=['order_id'])

        expected_ticket_arguments = {
            "Title": "Sol·licitud adsl {}".format(service_data.order_id),
            "Type": ADSLTicketConfiguration.type,
            "Queue": ADSLTicketConfiguration.queue,
            "State": ADSLTicketConfiguration.state,
            "SLA": False,
            "Service": False,
            "Priority": ADSLTicketConfiguration.priority,
            "CustomerUser": customer_data.id,
            "CustomerID": customer_data.id
        }

        ADSLTicket(service_data, customer_data)._build_ticket()
        MockTicket.assert_called_with(expected_ticket_arguments)

    @patch('otrs_somconnexio.otrs_models.provision_ticket.ProvisionArticle')
    def test_build_article(self, MockInternetArticle):
        customer_data = Mock(spec=[])
        service_data = Mock(spec=['order_id', 'notes'])

        mock_mobile_article = MockInternetArticle.return_value

        ADSLTicket(service_data, customer_data)._build_article()

        MockInternetArticle.assert_called_with(
            'adsl', 
            service_data.order_id, 
            service_data.notes
        )
        mock_mobile_article.call.assert_called_once()

    @patch('otrs_somconnexio.otrs_models.adsl_ticket.ADSLDynamicFields')
    def test_build_dynamic_fields(self, MockADSLDynamicFields):
        customer_data = Mock(spec=[])
        service_data = Mock(spec=['order_id'])

        mock_adsl_dynamic_fields = MockADSLDynamicFields.return_value

        ADSLTicket(service_data, customer_data). _build_dynamic_fields()

        MockADSLDynamicFields.assert_called_with(
            service_data,
            customer_data,
            ADSLTicketConfiguration.process_id,
            ADSLTicketConfiguration.activity_id,
        )
        mock_adsl_dynamic_fields.all.assert_called_once()

    @patch('otrs_somconnexio.otrs_models.provision_ticket.OTRSClient')
    def test_create(self, MockOTRSClient):
        customer_data = Mock(spec=[
            'id',
            'phone',
            'first_name',
            'name',
            'vat_number',
        ])
        service_data = Mock(spec=[
            'order_id',
            'iban',
            'email',
            'previous_service',
            'phone_number',
            'previous_provider',
            'previous_owner_vat',
            'previous_owner_name',
            'previous_owner_surname',
            'previous_contract_address',
            'previous_contract_phone',
            'service_address',
            'service_city',
            'service_zip',
            'service_subdivision',
            'service_subdivision_code',
            'shipment_address',
            'shipment_city',
            'shipment_zip',
            'shipment_subdivision',
            'notes',
            'adsl_coverage',
            'mm_fiber_coverage',
            'vdf_fiber_coverage',
            'orange_fiber_coverage',
            'type',
            'landline_phone_number',
            'product',
            'previous_internal_provider',
        ])

        mock_otrs_client = Mock(spec=['create_otrs_process_ticket'])
        mock_otrs_client.create_otrs_process_ticket.return_value.id = 123
        mock_otrs_client.create_otrs_process_ticket.return_value.number = '#123'
        MockOTRSClient.return_value = mock_otrs_client

        ticket = ADSLTicket(service_data, customer_data)
        ticket.create()

        mock_otrs_client.create_otrs_process_ticket.assert_called_once()

        self.assertEqual(ticket.id, 123)
        self.assertEqual(ticket.number, '#123')
