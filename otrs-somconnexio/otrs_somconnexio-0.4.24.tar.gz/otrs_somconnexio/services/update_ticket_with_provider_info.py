from otrs_somconnexio.client import OTRSClient
from pyotrs.lib import DynamicField


class UpdateTicketWithProviderInfo:
    """
    Abstract service which updates an OTRS process ticket with an article and some DF.
    """

    ticket_id = ""
    df_dct = {}
    article = None

    def run(self):
        otrs_client = OTRSClient()

        dynamic_fields = self._df_list_from_dct(self.df_dct)

        pyOTRS_article = self.article.call()

        otrs_client.update_ticket(
            self.ticket_id,
            pyOTRS_article,
            dynamic_fields=dynamic_fields)

    def _df_list_from_dct(self, df_dct):

        dynamic_fields = []
        for key, value in df_dct.items():
            df = DynamicField(name=key, value=value)
            dynamic_fields.append(df)

        return dynamic_fields
