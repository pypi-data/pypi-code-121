import os

from pyotrs import Client
from pyotrs.lib import DynamicField
from pyotrs.lib import APIError, HTTPError, ResponseParseError, SessionNotCreated, ArgumentMissingError

from otrs_somconnexio.responses.ticket_creation import OTRSCreationTicketResponse
from otrs_somconnexio.otrs_models.process_ticket.internet import InternetProcessTicket
from otrs_somconnexio.otrs_models.process_ticket.mobile import MobileProcessTicket
from otrs_somconnexio.otrs_models.coverage_ticket import CoverageTicket
from otrs_somconnexio.otrs_models.service import Service
from otrs_somconnexio.exceptions import TicketNotCreated, ErrorCreatingSession, TicketNotFoundError


class OTRSClient():
    TICKET_CONNECTOR_CONFIG = {
        'Name': 'GenericTicketConnectorREST',
        'Config': {
            'SessionCreate': {'RequestMethod': 'POST',
                              'Route': '/Session',
                              'Result': 'SessionID'},
            'TicketCreate': {'RequestMethod': 'POST',
                             'Route': '/Ticket',
                             'Result': 'TicketID'},
            'TicketGet': {'RequestMethod': 'GET',
                          'Route': '/Ticket/:TicketID',
                          'Result': 'Ticket'},
            'TicketGetList': {'RequestMethod': 'GET',
                              'Route': '/TicketList',
                              'Result': 'Ticket'},
            'TicketSearch': {'RequestMethod': 'POST',
                             'Route': '/TicketSearch',
                             'Result': 'TicketID'},
            'TicketUpdate': {'RequestMethod': 'PATCH',
                             'Route': '/Ticket/:TicketID',
                             'Result': 'TicketID'},
        }
    }

    def __init__(self):
        self.client = self._create_client_with_session()

    @staticmethod
    def _password():
        return os.environ['OTRS_PASSW']

    @staticmethod
    def _user():
        return os.environ['OTRS_USER']

    @staticmethod
    def _url():
        return os.environ['OTRS_URL']

    def _create_client_with_session(self):
        """ Create a OTRS Client with session open to play calls.

        This method call to the OTRS API to create a session to play another requests with authentication done.
        Raise User errors to show the problem with the request if it is fault.

        Return a client with the session opens.
        """
        try:
            client = Client(
                baseurl=self._url(),
                username=self._user(),
                password=self._password(),
                webservice_config_ticket=self.TICKET_CONNECTOR_CONFIG
            )
            client.session_create()
        except (HTTPError, APIError, ResponseParseError) as error:
            raise ErrorCreatingSession(error.message)
        return client

    def create_otrs_process_ticket(self, ticket, article, dynamic_fields):
        """ Create a OTRS Process Ticket to manage the provisioning.

        This method call to the OTRS API to create a ticket with all the information of the econtract.
        If the Ticket is created, return the response to save the ID and the number in the EticomContract
        model to keep the relation between systems.
        Else, raise an error with the needed information to fix the EticomContract and rerun the process.

        TODO: In the future, this method enqueue a job to call the OTRS API in asynchronous process.
        """
        try:
            client_response = self.client.ticket_create(
                ticket=ticket,
                article=article,
                dynamic_fields=dynamic_fields)
        except (HTTPError, APIError, ResponseParseError, SessionNotCreated, ArgumentMissingError) as error:
            raise TicketNotCreated(error.message, dynamic_fields)
        return OTRSCreationTicketResponse(client_response)

    def get_otrs_process_ticket(self, ticket_id):
        """ Search a OTRS Process Ticket by ID.

        This method call to the OTRS API to search a ticket with all the information of the provisioning process.
        If the Ticket is founded, return the Ticket object.
        Else, raise an TicketNotFoundError with error message returned.

        Return a PyOTRS Ticket object.
        """
        ticket = self.client.ticket_get_by_id(ticket_id, dynamic_fields=True)
        if not ticket:
            raise TicketNotFoundError(ticket_id)
        return self._process_ticket_response(ticket)

    def search_tickets(self, **params):
        tickets = []

        ticket_ids = self.client.ticket_search(**params)

        for ticket_id in ticket_ids:
            ticket = self.client.ticket_get_by_id(ticket_id, dynamic_fields=True)
            tickets.append(self._process_ticket_response(ticket))

        return tickets

    def search_coverage_tickets_by_email(self, email):
        df_process_id = {
            "name": "ProcessManagementProcessID",
            "value": "Process-be8cf222949132c9fae1bb74615a5ae4"
        }

        tickets = self.search_tickets(
            dynamic_fields=[
                DynamicField(df_process_id["name"], search_patterns=[df_process_id["value"]]),
                DynamicField("correuElectronic", search_patterns=[email])
            ]
        )
        return [CoverageTicket(t) for t in tickets]

    def update_ticket(self, ticket_id, article, dynamic_fields=[]):
        self.client.ticket_update(
            ticket_id,
            article,
            dynamic_fields=dynamic_fields
        )

    def _process_ticket_response(self, ticket):
        service = Service(ticket)
        if service.is_mobile():
            return MobileProcessTicket(ticket, service)
        return InternetProcessTicket(ticket, service)
