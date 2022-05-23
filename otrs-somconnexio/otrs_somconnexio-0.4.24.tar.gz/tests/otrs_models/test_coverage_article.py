# coding: utf-8
import unittest
from mock import Mock

from pyotrs.lib import Article
from otrs_somconnexio.otrs_models.coverage_article import CoverageArticle
from otrs_somconnexio.otrs_models.coverage_ticket import CoverageTicket


class CoverageArticleTestCase(unittest.TestCase):

    def setUp(self):
        ticket = Mock(spec=['response'])
        ticket.response = Mock(spec=['dynamic_field_get'])
        df_tipusVia = Mock(spec=['value'])
        df_tipusVia.value = 'street'

        def dynamic_field_side_effect(field_name):
            if field_name == 'tipusVia':
                return df_tipusVia
        ticket.response.dynamic_field_get.side_effect = dynamic_field_side_effect
        self.coverage_ticket = CoverageTicket(ticket)

    def test_call(self):
        coverage_article = CoverageArticle(self.coverage_ticket).call()

        self.assertIsInstance(coverage_article, Article)

    def test_call_Subject(self):
        coverage_article = CoverageArticle(self.coverage_ticket).call()

        self.assertEqual(coverage_article.field_get("Subject"), "Sol·licitud cobertura")

    def test_call_Body(self):
        coverage_article = CoverageArticle(self.coverage_ticket).call()

        self.assertEqual(coverage_article.field_get("Body"), "tipusVia: street\n")

    def test_call_ContentType(self):
        coverage_article = CoverageArticle(self.coverage_ticket).call()

        self.assertEqual(coverage_article.field_get("ContentType"), "text/plain; charset=utf8")
