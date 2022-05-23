# coding: utf-8
from pyotrs.lib import DynamicField

from otrs_somconnexio.otrs_models.internet_dynamic_fields import InternetDynamicFields


class ADSLDynamicFields(InternetDynamicFields):

    def _build_specific_broadband_service_dynamic_fields(self):
        """ Return list of OTRS DynamicFields to create a OTRS Process Ticket from Eticom Contract.
        Return only the specifics fields of ADSL Ticket. """
        return [
            self._df_landline_number(),
        ]

    def _df_landline_number(self):
        return DynamicField(name="mantenirFix", value=self.service_data.landline_phone_number)
