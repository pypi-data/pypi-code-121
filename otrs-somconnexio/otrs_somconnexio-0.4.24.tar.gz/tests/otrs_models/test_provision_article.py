# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.provision_article import ProvisionArticle 


class ProvisionArticleTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.otrs_models.abstract_article.Article')
    def test_call_with_notes(self, MockArticle):

        expected_article_arguments = {
            "Subject": "Sol·licitud a b",
            "Body": "c",
            "ContentType": "text/plain; charset=utf8",
            "IsVisibleForCustomer": "0",
        }
        ProvisionArticle(service_type='a', order_id='b', notes='c').call()
        MockArticle.assert_called_once_with(expected_article_arguments)

    @patch('otrs_somconnexio.otrs_models.abstract_article.Article')
    def test_call_without_notes(self, MockArticle):

        expected_article_arguments = {
            "Subject": "Sol·licitud a b",
            "Body": "",
            "ContentType": "text/plain; charset=utf8",
            "IsVisibleForCustomer": "1",
        }
        ProvisionArticle(service_type='a', order_id='b', notes='').call()
        MockArticle.assert_called_once_with(expected_article_arguments)
