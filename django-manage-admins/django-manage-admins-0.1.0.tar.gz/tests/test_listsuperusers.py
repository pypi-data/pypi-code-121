from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .factories import UserFactory


class TestListSuperusers(TestCase):
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "list_superusers",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_command_exists(self):
        """just make sure the command even exists"""
        out = self.call_command()
        self.assertNotEqual(out, "")

    def test_includes_superuser(self):
        u = UserFactory(is_superuser=True)
        out = self.call_command()
        self.assertTrue(u.username in out)

    def test_does_not_include_non_superusers(self):
        u = UserFactory(is_superuser=False)
        out = self.call_command()
        self.assertFalse(u.username in out)

    def test_only_includes_active_superusers(self):
        u_active = UserFactory(is_superuser=True, is_active=True)
        u_inactive = UserFactory(is_superuser=True, is_active=False)

        out = self.call_command()

        self.assertTrue(u_active.username in out)
        self.assertFalse(
            u_inactive.username in out, "inactive superusers should not be listed"
        )

    def test_alphabetical_order(self):
        # create them in non-alphabetical order
        UserFactory(username="b_user", is_superuser=True),
        UserFactory(username="c_user", is_superuser=True),
        UserFactory(username="a_user", is_superuser=True),

        out = self.call_command()

        self.assertTrue("a_user\nb_user\nc_user" in out)
