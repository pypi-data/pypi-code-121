# coding: utf-8
from pyotrs.lib import DynamicField

from otrs_somconnexio.otrs_models.internet_dynamic_fields import InternetDynamicFields


class FiberDynamicFields(InternetDynamicFields):

    def _build_specific_broadband_service_dynamic_fields(self):
        """ Return list of OTRS DynamicFields to create a OTRS Process Ticket from service data and customer data.
        Return only the specifics fields of Fiber Ticket. """
        return [
            self._df_previous_contract_pon(),
            self._df_previous_contract_fiber_speed()
        ]

    def _df_previous_contract_pon(self):
        return DynamicField(name="ponAntic", value=self.service_data.previous_contract_pon)

    def _df_previous_contract_fiber_speed(self):
        return DynamicField(
            name="velocitatSollicitadaContracteAnteriorCU",
            value=self.service_data.previous_contract_fiber_speed
        )
