# coding: utf-8
from otrs_somconnexio.otrs_models.coverage_article import CoverageArticle
from otrs_somconnexio.client import OTRSClient


class UpdateProcessTicketWithCoverageTicketsInfoService:
    """
    Update the process ticket adding articles with the coverage data.

    Receives a TicketID (provisioning process ticket) and an email.
    Finds coverage tickets by email and creates articles with the information
    required to update the provisioning process ticket.
    """
    def __init__(self, ticket_id):
        self.ticket_id = ticket_id
        self.otrs_client = OTRSClient()

    def run(self, email):
        coverage_tickets = self.otrs_client.search_coverage_tickets_by_email(email)
        for ticket in coverage_tickets:
            article = CoverageArticle(ticket).call()
            self.otrs_client.update_ticket(self.ticket_id, article)
