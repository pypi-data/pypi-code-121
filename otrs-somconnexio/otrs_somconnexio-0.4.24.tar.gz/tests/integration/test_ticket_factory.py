import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.ticket_factory import TicketFactory
from otrs_somconnexio.otrs_models.adsl_ticket import ADSLTicket
from otrs_somconnexio.otrs_models.fiber_ticket import FiberTicket
from otrs_somconnexio.otrs_models.mobile_ticket import MobileTicket


class TicketFactoryIntegrationTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.otrs_models.provision_ticket.OTRSClient')
    def test_create_mobile_ticket_factory(self, MockOTRSClient):
        mobile_data = Mock(spec=[
            'order_id',
            'type',
            'iban',
            'email',
            'phone_number',
            'sc_icc',
            'icc',
            'type',
            'previous_provider',
            'previous_owner_name',
            'previous_owner_surname',
            'previous_owner_vat',
            'product',
            'notes',
            'has_sim',
            'delivery_street',
            'delivery_city',
            'delivery_zip_code',
            'delivery_state',
        ])
        customer_data = Mock(spec=[
            'id',
            'first_name',
            'name',
            'vat_number',
            'phone',
            'street',
            'city',
            'zip',
            'subdivision'])

        mobile_data.service_type = 'mobile'

        otrs_process_ticket = Mock(spec=['id'])
        otrs_process_ticket.id = 234

        mock_otrs_client = Mock(spec=['create_otrs_process_ticket'])
        mock_otrs_client.create_otrs_process_ticket.return_value = otrs_process_ticket
        MockOTRSClient.return_value = mock_otrs_client

        ticket = TicketFactory(
            service_data=mobile_data,
            customer_data=customer_data
        ).build()
        ticket.create()

        self.assertEquals(ticket.id, 234)
        self.assertIsInstance(ticket, MobileTicket)

    @patch('otrs_somconnexio.otrs_models.provision_ticket.OTRSClient')
    def test_create_adsl_ticket_factory(self, MockOTRSClient):
        service_data = Mock(spec=[
            'order_id',
            'type',
            'iban',
            'email',
            'phone_number',
            'previous_provider',
            'previous_owner_name',
            'previous_owner_surname',
            'previous_owner_vat',
            'previous_service',
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
        customer_data = Mock(spec=['id', 'first_name', 'name', 'vat_number', 'phone'])

        service_data.service_type = 'adsl'

        otrs_process_ticket = Mock(spec=['id'])
        otrs_process_ticket.id = 234

        mock_otrs_client = Mock(spec=['create_otrs_process_ticket'])
        mock_otrs_client.create_otrs_process_ticket.return_value = otrs_process_ticket
        MockOTRSClient.return_value = mock_otrs_client

        ticket = TicketFactory(
            service_data,
            customer_data
        ).build()
        ticket.create()
        ticket.create()

        self.assertIsInstance(ticket, ADSLTicket)
        self.assertEquals(ticket.id, 234)

    @patch('otrs_somconnexio.otrs_models.provision_ticket.OTRSClient')
    def test_create_fiber_ticket_factory(self, MockOTRSClient):
        service_data = Mock(spec=[
            'order_id',
            'previous_contract_pon',
            'previous_contract_fiber_speed',
            'previous_contract_address',
            'previous_contract_phone',
            'type',
            'iban',
            'email',
            'phone_number',
            'previous_provider',
            'previous_owner_name',
            'previous_owner_surname',
            'previous_owner_vat',
            'previous_service',
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
            'product',
            'previous_internal_provider',
        ])
        customer_data = Mock(spec=['id', 'first_name', 'name', 'vat_number', 'phone'])

        service_data.service_type = 'fiber'

        otrs_process_ticket = Mock(spec=['id'])
        otrs_process_ticket.id = 234

        mock_otrs_client = Mock(spec=['create_otrs_process_ticket'])
        mock_otrs_client.create_otrs_process_ticket.return_value = otrs_process_ticket
        MockOTRSClient.return_value = mock_otrs_client

        ticket = TicketFactory(
            service_data,
            customer_data
        ).build()
        ticket.create()

        self.assertIsInstance(ticket, FiberTicket)
        self.assertEquals(ticket.id, 234)
