# coding: utf-8
from otrs_somconnexio.otrs_models.provision_ticket import ProvisionTicket
from otrs_somconnexio.otrs_models.router_4G_dynamic_fields import Router4GDynamicFields
from otrs_somconnexio.otrs_models.configurations.router_4G_ticket import Router4GTicketConfiguration


class Router4GTicket(ProvisionTicket):

    def __init__(self, service_data, customer_data):
        self.service_data = service_data
        self.customer_data = customer_data
        self.otrs_configuration = Router4GTicketConfiguration()

    def service_type(self):
        return '4G'

    def _build_dynamic_fields(self):
        # Router 4G does not have specific 4G fields so far
        return Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self._ticket_process_id(),
            self._ticket_activity_id()
        ).all()
