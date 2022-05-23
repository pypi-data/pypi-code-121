# coding: utf-8
from otrs_somconnexio.otrs_models.provision_ticket import ProvisionTicket
from otrs_somconnexio.otrs_models.adsl_dynamic_fields import ADSLDynamicFields
from otrs_somconnexio.otrs_models.configurations.adsl_ticket import ADSLTicketConfiguration


class ADSLTicket(ProvisionTicket):

    def __init__(self, service_data, customer_data, otrs_configuration=None):
        self.service_data = service_data
        self.customer_data = customer_data
        self.otrs_configuration = ADSLTicketConfiguration(otrs_configuration)

    def service_type(self):
        return 'adsl'

    def _build_dynamic_fields(self):
        return ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self._ticket_process_id(),
            self._ticket_activity_id()
        ).all()
