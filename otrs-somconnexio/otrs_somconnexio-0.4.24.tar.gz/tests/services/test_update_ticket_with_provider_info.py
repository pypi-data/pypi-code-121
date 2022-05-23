import unittest
from mock import Mock, patch

from pyotrs.lib import DynamicField
from otrs_somconnexio.client import OTRSClient
from otrs_somconnexio.services.update_ticket_with_provider_info import \
    UpdateTicketWithProviderInfo

class FakeUpdateTicketService(UpdateTicketWithProviderInfo):
    """
    Custom class which inherits from UpdateTicketWithProviderInfo.
    Intended only for tests purposes.
    """

    def __init__(self, ticket_id, article, df_dct):
        self.ticket_id = ticket_id
        self.article = article
        self.df_dct = df_dct

class UpdateTicketWithProviderInfoTestCase(unittest.TestCase):

    def setUp(self):
        self.ticket_id = '00001'
        self.test_name = 'test_name'
        self.test_value = 'test_value'
        self.expected_df = DynamicField(name=self.test_name, value=self.test_value)
        self.pyOTRS_article = object()
        self.article = Mock(spec=['call'])
        self.df_dct = {self.test_name: self.test_value}

    @patch('otrs_somconnexio.services.update_ticket_with_provider_info.OTRSClient',
           return_value=Mock(spec=['update_ticket']))
    @patch('otrs_somconnexio.services.update_ticket_with_provider_info.DynamicField')
    def test_run(self, MockDF, MockOTRSClient):

        def mock_df_side_effect(name, value):
            if name == self.test_name and value == self.test_value:
                return self.expected_df

        MockDF.side_effect = mock_df_side_effect
        self.article.call.return_value = self.pyOTRS_article

        FakeUpdateTicketService(self.ticket_id, self.article, self.df_dct).run()

        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            self.ticket_id,
            self.pyOTRS_article,
            dynamic_fields=[self.expected_df]
        )