# coding: utf-8
from otrs_somconnexio.otrs_models.configurations.fiber_ticket import FiberTicketConfiguration
from otrs_somconnexio.otrs_models.fiber_dynamic_fields import FiberDynamicFields
from otrs_somconnexio.otrs_models.provision_ticket import ProvisionTicket


class FiberTicket(ProvisionTicket):

    def __init__(self, service_data, customer_data, otrs_configuration=None):
        self.service_data = service_data
        self.customer_data = customer_data
        self.otrs_configuration = FiberTicketConfiguration(otrs_configuration)

    def service_type(self):
        return 'fiber'

    def _build_dynamic_fields(self):
        return FiberDynamicFields(
            self.service_data,
            self.customer_data,
            self._ticket_process_id(),
            self._ticket_activity_id()
        ).all()
