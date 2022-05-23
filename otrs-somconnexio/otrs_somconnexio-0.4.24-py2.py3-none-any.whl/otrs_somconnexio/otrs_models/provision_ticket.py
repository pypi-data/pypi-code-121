# coding: utf-8
from pyotrs.lib import Ticket

from otrs_somconnexio.client import OTRSClient
from otrs_somconnexio.otrs_models.provision_article import ProvisionArticle


class ProvisionTicket():
    def create(self):
        self.otrs_ticket = OTRSClient().create_otrs_process_ticket(
            self._build_ticket(),
            self._build_article(),
            self._build_dynamic_fields())

    @property
    def id(self):
        return self.otrs_ticket.id

    @property
    def number(self):
        return self.otrs_ticket.number

    def _build_ticket(self):
        return Ticket({
            "Title": "Sol·licitud {} {}".format(
                self.service_type(),
                self.service_data.order_id
            ),
            "Type": self._ticket_type(),
            "Queue": self._ticket_queue(),
            "State": self._ticket_state(),
            "Priority": self._ticket_priority(),
            "CustomerUser": self._customer_id(),
            "CustomerID": self._customer_id(),
            "Service": self._ticket_service(),
            "SLA": self._ticket_SLA(),
        })

    def _build_article(self):
        provision_article = ProvisionArticle(
            self.service_type(),
            self.service_data.order_id,
            self.service_data.notes,
        )
        return provision_article.call()

    def _ticket_type(self):
        return self.otrs_configuration.type

    def _ticket_queue(self):
        return self.otrs_configuration.queue

    def _ticket_state(self):
        return self.otrs_configuration.state

    def _ticket_priority(self):
        return self.otrs_configuration.priority

    def _ticket_activity_id(self):
        return self.otrs_configuration.activity_id

    def _ticket_process_id(self):
        return self.otrs_configuration.process_id

    def _ticket_service(self):
        if hasattr(self.otrs_configuration, "service"):
            return self.otrs_configuration.service
        else:
            return False

    def _ticket_SLA(self):
        if hasattr(self.otrs_configuration, "SLA"):
            return self.otrs_configuration.SLA
        else:
            return False

    def _customer_id(self):
        return self.customer_data.id
