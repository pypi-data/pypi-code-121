# coding: utf-8

from otrs_somconnexio.client import OTRSClient
from otrs_somconnexio.otrs_models.vf_provisioning_article import VfProvisioningArticle


class UpdateProcessTicketWithVfProvisioning:
    """
    Update the ticket process adding articles with the VF spreadsheet provisioning data.

    Receives a ticket_id (str) and its provisioning data (as dict) provided by the changes in
    Vodaphone's spreadsheet.
    When this process runs, it creates an article with this information and it sends it to OTRS,
    updating the ticket provisioning process.
    """

    def __init__(self, ticket_id, provisioning):
        self.ticket_id = ticket_id
        self.provisioning = provisioning

    def run(self):
        otrs_client = OTRSClient()

        article = VfProvisioningArticle(self.provisioning).call()
        otrs_client.update_ticket(self.ticket_id, article)
