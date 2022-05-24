import unittest

from modela import *
import pprint


class Test_Modela_userroleclass(unittest.TestCase):
    """Tests for `modela.training.UserRoleClass`"""

    @classmethod
    def setUpClass(cls):
        cls.modela = Modela(port_forward=True)

    @classmethod
    def tearDownClass(cls):
        cls.modela.close()

    def test_list(self):
        assert len(self.modela.UserRoleClasses.list("default-tenant")) >= 1

    def test_get(self):
        role = self.modela.UserRoleClass("default-tenant", "administrator")
        assert len(role.rules) > 0
        assert Verb.All in role.rule(ResourceKind.Study).Verbs

    def test_write(self):
        role = self.modela.UserRoleClass("default-tenant", "business")
        role.allow_verb(ResourceKind.Job, Verb.Watch)
        assert Verb.Watch in role.rule(ResourceKind.Job).Verbs
        role.allow_all(ResourceKind.Job)
        assert Verb.All in role.rule(ResourceKind.Job).Verbs
        role.deny_verb(ResourceKind.Job, Verb.Delete)
        assert set(role.rule(ResourceKind.Job).Verbs) == {Verb.Patch, Verb.Watch, Verb.Update, Verb.Create, Verb.List, Verb.Get}
        role.deny_all(ResourceKind.Job)
        assert len(role.rule(ResourceKind.Job).Verbs) == 0