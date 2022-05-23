import unittest
from mock import Mock

from otrs_somconnexio.otrs_models.coverage_ticket import CoverageTicket


class CoverageTicketTestCase(unittest.TestCase):

    def setUp(self):
        self.coverage_ticket_response = Mock(spec=[])
        self.coverage_ticket_response.response = Mock(spec=["dynamic_field_get"])

        def dynamic_field_get_side_effect(name):
            df_value = Mock(spec=[])
            if name == "foo":
                df_value.value = "bar"
            elif name == "bar":
                df_value.value = "foo"

            return df_value
        self.coverage_ticket_response.response.dynamic_field_get.side_effect = dynamic_field_get_side_effect

    def test_get_foo(self):
        coverage_ticket = CoverageTicket(self.coverage_ticket_response)

        self.assertEqual(coverage_ticket.foo, "bar")

    def test_get_bar(self):
        coverage_ticket = CoverageTicket(self.coverage_ticket_response)

        self.assertEqual(coverage_ticket.bar, "foo")
