from ..sc_test_case import SCTestCase
from psycopg2 import IntegrityError
import odoo


class TestPreviousProvider(SCTestCase):

    @odoo.tools.mute_logger("odoo.sql_db")
    def test_create_without_name(self):
        dct = {"code": "hola", "mobile": True, "broadband": False}

        self.assertRaises(
            IntegrityError,
            self.env['previous.provider'].create,
            dct
        )

    @odoo.tools.mute_logger("odoo.sql_db")
    def test_delete_name(self):
        self.previous_provider = self.browse_ref('somconnexio.previousprovider56')

        self.assertRaises(
            IntegrityError,
            self.previous_provider.write,
            {"name": False}
        )
