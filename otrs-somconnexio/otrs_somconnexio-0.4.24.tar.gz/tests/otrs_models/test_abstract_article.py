import unittest
from mock import patch

from otrs_somconnexio.otrs_models.abstract_article import AbstractArticle


class FakeArticle(AbstractArticle):
    """
    Custom class which inherits from AbstractArticle.
    Intended only for tests purposes.
    """
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body


class AbstractArticleTestCase(unittest.TestCase):

    @patch('otrs_somconnexio.otrs_models.abstract_article.Article')
    def test_call(self, MockArticle):

        expected_article_arguments = {
            "Subject": "test_subject",
            "Body": "test_body",
            "ContentType": "text/plain; charset=utf8",
            "IsVisibleForCustomer": "1",
        }

        FakeArticle("test_subject", "test_body").call()
        MockArticle.assert_called_once_with(expected_article_arguments)
