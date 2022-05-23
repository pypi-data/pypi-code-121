# coding: utf-8
from otrs_somconnexio.otrs_models.internet_dynamic_fields import InternetDynamicFields


class Router4GDynamicFields(InternetDynamicFields):

    def _build_specific_broadband_service_dynamic_fields(self):
        """ Return list of OTRS DynamicFields to create a OTRS Process Ticket from Eticom Contract.
        Return only the specifics fields of Router 4G Ticket. """
        return []
