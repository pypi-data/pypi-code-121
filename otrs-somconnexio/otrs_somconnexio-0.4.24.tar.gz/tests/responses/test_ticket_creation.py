import unittest

from otrs_somconnexio.responses.ticket_creation import OTRSCreationTicketResponse

from tests.data.otrs_raw_responses import OTRSTicketCreateResponse


class TicketCreationResponseTestCase(unittest.TestCase):
    'Test Ticket creation response parser'

    def test_ticket_creation_parse_response_id(self):
        'Instantiate a OTRSCreationTicketResponse from otrs_ticket_creation_response'
        ticket = OTRSCreationTicketResponse(OTRSTicketCreateResponse)

        self.assertEqual("1", ticket.id)

    def test_ticket_creation_parse_response_number(self):
        'Instantiate a OTRSCreationTicketResponse from otrs_ticket_creation_response'
        ticket = OTRSCreationTicketResponse(OTRSTicketCreateResponse)

        self.assertEqual("2018081300000001", ticket.number)

    def test_ticket_creation_parse_response_article_id(self):
        'Instantiate a OTRSCreationTicketResponse from otrs_ticket_creation_response'
        ticket = OTRSCreationTicketResponse(OTRSTicketCreateResponse)

        self.assertEqual("11", ticket.article_id)
