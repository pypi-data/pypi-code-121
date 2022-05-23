# coding: utf-8
import os
import unittest
from mock import Mock, patch
from pyotrs.lib import DynamicField

from otrs_somconnexio.otrs_models.coverage_ticket import CoverageTicket

from otrs_somconnexio.services.update_process_ticket_with_coverage_tickets_info_service import \
    UpdateProcessTicketWithCoverageTicketsInfoService

USER = 'user'
PASSW = 'passw'
URL = 'https://otrs-url.coop/'


class UpdateTicketWithCoverageTicketInfoTestCase(unittest.TestCase):

    @patch.dict(os.environ, {
        'OTRS_USER': USER,
        'OTRS_PASSW': PASSW,
        'OTRS_URL': URL
    })
    @patch('otrs_somconnexio.client.Client', return_value=Mock(
        spec=['session_create', 'ticket_update', 'ticket_search', 'ticket_get_by_id']
    ))
    @patch('otrs_somconnexio.otrs_models.abstract_article.Article')
    def test_run(self, MockArticle, MockClient):
        process_ticket_id = 123
        coverage_ticket_id = 456
        email = 'email@email.com'
        ticket = Mock(spec=['response'])
        ticket.response = Mock(spec=['dynamic_field_get'])

        def get_df_side_effect(name):
            return DynamicField(name, 'foo')

        ticket.response.dynamic_field_get.side_effect = get_df_side_effect
        coverage_ticket = CoverageTicket(ticket)

        coverage_article = object()
        MockArticle.return_value = coverage_article

        def ticket_search_side_effect(dynamic_fields):
            if len(dynamic_fields) != 2:
                return []
            if dynamic_fields[0].search_patterns == ["Process-be8cf222949132c9fae1bb74615a5ae4"] \
                and dynamic_fields[1].search_patterns == [email]:
                    return [coverage_ticket_id]
            return []

        MockClient.return_value.ticket_search.side_effect = ticket_search_side_effect
        MockClient.return_value.ticket_get_by_id.return_value = ticket.response

        UpdateProcessTicketWithCoverageTicketsInfoService(process_ticket_id).run(email)

        MockClient.return_value.ticket_get_by_id.assert_called_with(coverage_ticket_id, dynamic_fields=True)

        MockClient.return_value.ticket_update.assert_called_with(process_ticket_id, coverage_article, dynamic_fields=[])
        MockArticle.assert_called_with({
            "Subject": "Sol·licitud cobertura",
            "Body": "tipusVia: foo\nnomVia: foo\nnumero: foo\nbloc: foo\nportal: foo\npis: foo\nescala: foo\nporta: foo\npoblacioServei: foo\nprovinciaServei: foo\ncodiProvinciaServei: foo\nCPservei: foo\naltresCobertura: foo\ncoberturaADSL: foo\ncoberturaFibraMM: foo\ncoberturaFibraVdf: foo\ncoberturaFibraOrange: foo\nIDhogar: foo\n",  # noqa
            "ContentType": "text/plain; charset=utf8",
            "IsVisibleForCustomer": "1",
        })
