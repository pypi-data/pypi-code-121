import unittest
from datetime import datetime
from mock import Mock

from pyotrs import Ticket

from otrs_somconnexio.otrs_models.process_ticket.mobile import MobileProcessTicket

from tests.data.otrs_raw_responses import OTRSTicketGetResponse


class MobileTicketResponseTestCase(unittest.TestCase):
    def test_otrs_ticket_get_parse_response(self):
        'Instantiate a OTRSTicket from otrs_ticket_get_response'
        OTRSTicketGetResponse['DynamicField'] = [
            {"Name": "IDContracte", "Value": "1022"},
            {"Name": "nomSoci", "Value": "Pere"},
            {"Name": "cognom1", "Value": "Pablo"},
            {"Name": "NIFNIESoci", "Value": "123456789G"},
            {"Name": "NIFNIEtitular", "Value": "123456789F"},
            {"Name": "IBAN", "Value": "ES9000246912501234567891"},
            {"Name": "dataIniciFacturacio", "Value": "2018-12-10 00:00:00"},
        ]

        ticket = MobileProcessTicket(Ticket(OTRSTicketGetResponse), Mock(spec=[]))

        # Ticket
        self.assertEqual("2", ticket.id)
        self.assertEqual("2018081300000002", ticket.number)

        # Contract
        self.assertEqual("1022", ticket.contract_id)

        # Soci
        self.assertEqual("Pere", ticket.partner_name)
        self.assertEqual("Pablo", ticket.partner_surname)
        self.assertEqual("123456789G", ticket.partner_vat_number)
        self.assertEqual("123456789F", ticket.owner_vat_number)

        self.assertEqual("ES9000246912501234567891", ticket.iban)

        expected_date = datetime.strptime("2018-12-10 00:00:00", "%Y-%m-%d %H:%M:%S")
        self.assertEqual(expected_date, ticket.invoices_start_date)

    def test_otrs_ticket_get_parse_response_mobile(self):
        OTRSTicketGetResponse['DynamicField'] = [
            {"Name": "TecDelServei", "Value": "Mobile"},
            {"Name": "liniaMobil", "Value": "123456789"},
            {"Name": "ICCSC", "Value": "1234"},
            {"Name": "NIFNIESoci", "Value": "52472919Y"},
            {"Name": "dadesMobil", "Value": "2GB"},
            {"Name": "minutsMobil", "Value": "100min"},
            {"Name": "productMobil", "Value": "100min1GB"},
        ]
        service_mock = Mock(spec=['is_mobile'])
        service_mock.is_mobile = True
        ticket = MobileProcessTicket(
            Ticket(OTRSTicketGetResponse),
            service_mock
        )

        self.assertEqual("mobile", ticket.service_technology)
        self.assertEqual("123456789", ticket.msisdn)
        self.assertEqual("1234", ticket.icc)
        self.assertEqual("2GB", ticket.data)
        self.assertEqual("100", ticket.minutes)
        self.assertEqual("100min1GB", ticket.product_code)

    def test_otrs_ticket_is_confirmed(self):
        'Instantiate a OTRSTicket from otrs_ticket_get_response and check if is confirmed'
        OTRSTicketGetResponse['State'] = "closed successful"
        service_mock = Mock(spec=['is_mobile'])
        service_mock.is_mobile = True
        ticket = MobileProcessTicket(
            Ticket(OTRSTicketGetResponse),
            service_mock
        )

        self.assertTrue(ticket.confirmed())

    def test_otrs_ticket_is_cancelled(self):
        'Instantiate a OTRSTicket from otrs_ticket_get_response and check if is cancelled'
        OTRSTicketGetResponse['State'] = "closed unsuccessful"
        service_mock = Mock(spec=['is_mobile'])
        service_mock.is_mobile = True
        ticket = MobileProcessTicket(
            Ticket(OTRSTicketGetResponse),
            service_mock
        )

        self.assertTrue(ticket.cancelled())

    def test_otrs_ticket_is_paused_without_coverage_adsl(self):
        """
        Instantiate an OTRSTicket from otrs_ticket_get_response and check if it's paused without coverage (ADSL service)
        """
        service_mock = Mock(spec=['is_mobile'])
        service_mock.is_mobile = True
        ticket = MobileProcessTicket(
            Ticket(OTRSTicketGetResponse),
            service_mock
        )

        self.assertFalse(ticket.paused_without_coverage())
