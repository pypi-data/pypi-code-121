# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.vf_provisioning_article import VfProvisioningArticle

class VfProvisioningArticleTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.otrs_models.abstract_article.Article')
    def test_call(self, MockArticle):

        fake_provisioning_dict = {
            'opportunity_id': '1-2HNXG6I',
            'offer': '961447541',
            'ticket': '1234'
        }
        expected_article_arguments = {
            "Subject": "Aprovisionament del tiquet de Vodafone 1234",
            "Body": "offer: 961447541\nopportunity_id: 1-2HNXG6I\nticket: 1234\n",
            "ContentType": "text/plain; charset=utf8",
            "IsVisibleForCustomer": "1",
        }
        VfProvisioningArticle(fake_provisioning_dict).call()
        MockArticle.assert_called_once_with(expected_article_arguments)
