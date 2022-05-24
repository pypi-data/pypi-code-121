import unittest
from modela.server import Modela

class TestModela_account(unittest.TestCase):
    """Tests for `modela` package."""

    @classmethod
    def setUpClass(cls):
        cls.modela = Modela(port_forward=True)

    @classmethod
    def tearDownClass(cls):
        cls.modela.close()

    def test_account_create(self):
        account = self.modela.Account(namespace="default-tenant", name="test")
        assert account != None
        account.submit(replace=True, password="test")

    def test_account_update(self):
        pass

    def test_account_get(self):
        account = self.modela.Account(namespace="default-tenant", name="admin")

    def test_account_delete(self):
        account = self.modela.Account(namespace="default-tenant", name="test")
        account.delete()

    def test_account_list(self):
        print(self.modela.Accounts.list("default-tenant"))



        
