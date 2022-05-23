# coding: utf-8
from otrs_somconnexio.otrs_models.configurations.mobile_ticket import MobileTicketConfiguration
from otrs_somconnexio.otrs_models.mobile_dynamic_fields import MobileDynamicFields
from otrs_somconnexio.otrs_models.provision_ticket import ProvisionTicket


class MobileTicket(ProvisionTicket):
    def __init__(self, service_data, customer_data, otrs_configuration=None):
        self.service_data = service_data
        self.customer_data = customer_data
        self.otrs_configuration = MobileTicketConfiguration(otrs_configuration)

    def service_type(self):
        return 'mobile'

    def _build_dynamic_fields(self):
        return MobileDynamicFields(
            self.service_data,
            self.customer_data,
            self._ticket_process_id(),
            self._ticket_activity_id()
        ).all()
