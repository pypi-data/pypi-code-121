import unittest

from mock import Mock, patch

from otrs_somconnexio.services.update_process_ticket_with_VF_provisioning import UpdateProcessTicketWithVfProvisioning


class UpdateProcessTicketWithVfProvisioningTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.services.update_process_ticket_with_VF_provisioning.OTRSClient', return_value=Mock(spec=['update_ticket']),
           )
    @patch('otrs_somconnexio.services.update_process_ticket_with_VF_provisioning.VfProvisioningArticle')
    def test_run(self, MockVfProvisioningArticle, MockOTRSClient):

        ticket_id = '2019070900000151'
        provisioning = {
            ticket_id: {
                'opportunity_id': '1-2HNXG6I',
                'offer': '961447541'
            }
        }
  
        mock_provisioning_article = Mock(spec=['call'])
        provisioning_article = object()

        def mock_provisioning_article_side_effect(provisioning_ticket):
            if provisioning_ticket == provisioning[ticket_id]:
                mock_provisioning_article.call.return_value = provisioning_article
                return mock_provisioning_article

        MockVfProvisioningArticle.side_effect = mock_provisioning_article_side_effect

        UpdateProcessTicketWithVfProvisioning(ticket_id, provisioning[ticket_id]).run()

        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            ticket_id,
            provisioning_article
        )
