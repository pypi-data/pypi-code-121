from datetime import datetime
import unittest
from mock import Mock

from pyotrs import Ticket

from otrs_somconnexio.otrs_models.process_ticket.internet import InternetProcessTicket

from tests.data.otrs_raw_responses import OTRSTicketGetResponse


class OTRSTicketResponseTestCase(unittest.TestCase):
    'Test OTRS Ticket response parser'

    def test_otrs_ticket_get_parse_response(self):
        'Instantiate a OTRSTicket from otrs_ticket_get_response'
        get_response = {
                "TicketID": "2",
                "TicketNumber": "2018081300000002",
                "State": "closed successful",
                "CustomerID": "example@mail.com",
                "DynamicField": [
                    {"Name": "ProcessManagementActivityID", "Value": "Activity-2add0d7a8235a9c91f8c594b199f6b89"},
                    {"Name": "ProcessManagementProcessID", "Value": "Process-441820b536cb5b9899d12f729e6f5e97"},
                    {"Name": "IDContracte", "Value": "1022"},
                    {"Name": "nomSoci", "Value": "Pere"},
                    {"Name": "cognom1", "Value": "Pablo"},
                    {"Name": "NIFNIESoci", "Value": "123456789"},
                    {"Name": "correuElectronic", "Value": "pere.pablo@email.coop"},     # Party
                    {"Name": "NIFNIEtitular", "Value": "123456789"},
                    {"Name": "IBAN", "Value": "ES9000246912501234567891"},
                    {"Name": "dataIniciFacturacio", "Value": "2018-12-10 00:00:00"},
                    ],
                }
        ticket = InternetProcessTicket(Ticket(get_response), None)

        # Ticket
        self.assertEqual("2", ticket.id)
        self.assertEqual("2018081300000002", ticket.number)

        # Contract
        self.assertEqual("1022", ticket.contract_id)

        # Soci
        self.assertEqual("Pere", ticket.partner_name)
        self.assertEqual("Pablo", ticket.partner_surname)
        self.assertEqual("123456789", ticket.partner_vat_number)
        self.assertEqual("123456789", ticket.owner_vat_number)

        self.assertEqual("ES9000246912501234567891", ticket.iban)

        expected_date = datetime.strptime("2018-12-10 00:00:00", "%Y-%m-%d %H:%M:%S")
        self.assertEqual(expected_date, ticket.invoices_start_date)

    def test_otrs_ticket_get_parse_response_adsl(self):
        OTRSTicketGetResponse['DynamicField'] = [
            {"Name": "TecDelServei", "Value": "ADSL"},
            {"Name": "telefonFixAssignat", "Value": "987654321"},
            {"Name": "serveiFix", "Value": "no_phone"},
            {"Name": "minutsInclosos", "Value": "100"},
            {"Name": "mantenirFix", "Value": "dont_apply"},
            {"Name": "productBA", "Value": "ADSL20+"},

            # Review with Pol
            # TODO: Quins son d'ADSL i quins son de Fibra??
            {"Name": "proveidorPrevi", "Value": "Cap"},
            {"Name": "direccioServei", "Value": "Street 1234"},
            {"Name": "poblacioServei", "Value": "Barcelona"},
            {"Name": "provinciaServei", "Value": "Barcelona"},
            {"Name": "codiProvinciaServei", "Value": "ES-B"},
            {"Name": "CPservei", "Value": "08123"},
            {"Name": "IDcomanda", "Value": "1234"},
            {"Name": "IDhogar", "Value": None},
            {"Name": "pon", "Value": "1907"},
            {"Name": "numAdministratiuJazztel", "Value": None},
            {"Name": "MACaddress", "Value": "123456789"},
            {"Name": "usuariEndpoint", "Value": "user"},
            {"Name": "contrasenyaEndpoint", "Value": "passw"},
            {"Name": "usuariPPP", "Value": "user"},
            {"Name": "serialNumber", "Value": "ababab"},
        ]
        service_mock = Mock(spec=['is_mobile'])
        service_mock.is_mobile = False
        ticket = InternetProcessTicket(
            Ticket(OTRSTicketGetResponse),
            service_mock
        )

        self.assertEqual("adsl", ticket.service_technology)
        self.assertEqual("987654321", ticket.msisdn)
        self.assertEqual("no_phone", ticket.landline)
        self.assertEqual("100", ticket.landline_minutes)
        self.assertEqual("dont_apply", ticket.keep_landline_number)
        self.assertEqual("ADSL20+", ticket.product_code)

        # Review
        self.assertEqual("Cap", ticket.previous_provider)
        self.assertEqual("Street 1234", ticket.service_address)
        self.assertEqual("Barcelona", ticket.service_city)
        self.assertEqual("Barcelona", ticket.service_subdivision)
        self.assertEqual("ES-B", ticket.service_subdivision_code)
        self.assertEqual("08123", ticket.service_zip)
        self.assertEqual("1234", ticket.extid)
        self.assertEqual("1907", ticket.reference)
        self.assertEqual("123456789", ticket.mac_address)
        self.assertEqual("user", ticket.endpoint_user)
        self.assertEqual("passw", ticket.endpoint_password)
        self.assertEqual("user", ticket.ppp_user)
        self.assertEqual("ababab", ticket.ppp_password)

    def test_otrs_ticket_get_parse_response_fibre(self):
        OTRSTicketGetResponse['DynamicField'] = [
            {"Name": "productBA", "Value": "Fibra100"},
            {"Name": "TecDelServei", "Value": "Fibra"},
            {"Name": "telefonFixAssignat", "Value": "987654321"},
            {"Name": "velocitatSollicitada", "Value": "100"},
        ]
        service_mock = Mock(spec=['is_mobile'])
        service_mock.is_mobile = False
        ticket = InternetProcessTicket(
            Ticket(OTRSTicketGetResponse),
            service_mock
        )

        self.assertEqual("fiber", ticket.service_technology)
        self.assertEqual("987654321", ticket.msisdn)
        self.assertEqual("100", ticket.speed)
        self.assertEqual("Fibra100", ticket.product_code)

    def test_otrs_ticket_is_confirmed(self):
        'Instantiate a OTRSTicket from otrs_ticket_get_response and check if is confirmed'
        OTRSTicketGetResponse['State'] = "closed successful"
        service_mock = Mock(spec=['is_mobile'])
        service_mock.is_mobile = False
        ticket = InternetProcessTicket(
            Ticket(OTRSTicketGetResponse),
            service_mock
        )

        self.assertTrue(ticket.confirmed())

    def test_otrs_ticket_is_cancelled(self):
        'Instantiate a OTRSTicket from otrs_ticket_get_response and check if is cancelled'
        OTRSTicketGetResponse['State'] = "closed unsuccessful"
        service_mock = Mock(spec=['is_mobile'])
        service_mock.is_mobile = False
        ticket = InternetProcessTicket(
            Ticket(OTRSTicketGetResponse),
            service_mock
        )

        self.assertTrue(ticket.cancelled())

    def test_otrs_ticket_is_paused_without_coverage_fibre(self):
        """
        Instantiate an OTRSTicket from otrs_ticket_get_response and check if it's paused without coverage (Fibre service)
        """
        OTRSTicketGetResponse['DynamicField'] = [
            {"Name": "TecDelServei", "Value": "Fibra"},
            {"Name": "coberturaFibra", "Value": "fibraIndirecta"},
            {"Name": "coberturaFibraMM", "Value": "NoFibra"},
            {"Name": "coberturaFibraVdf", "Value": "NoFibraVdf"},
        ]
        service_mock = Mock(spec=['is_mobile', 'has_coverage'])
        service_mock.is_mobile = False
        service_mock.has_coverage.return_value = False
        ticket = InternetProcessTicket(
            Ticket(OTRSTicketGetResponse),
            service_mock
        )

        self.assertTrue(ticket.paused_without_coverage())

    def test_otrs_ticket_is_paused_without_coverage_adsl(self):
        """
        Instantiate an OTRSTicket from otrs_ticket_get_response and check if it's paused without coverage (ADSL service)
        """
        OTRSTicketGetResponse['DynamicField'] = [
            {"Name": "TecDelServei", "Value": "ADSL"},
            {"Name": "coberturaADSL", "Value": "NoServei"},
        ]

        service_mock = Mock(spec=['is_mobile', 'has_coverage'])
        service_mock.is_mobile = False
        service_mock.has_coverage.return_value = False
        service_mock.is_mobile = False
        ticket = InternetProcessTicket(
            Ticket(OTRSTicketGetResponse),
            service_mock
        )

        self.assertTrue(ticket.paused_without_coverage())
