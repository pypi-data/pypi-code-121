from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .factories import UserFactory


class TestListStaff(TestCase):
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "list_staff",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_command_exists(self):
        """just make sure the command even exists"""
        self.call_command()

    def test_includes_staff(self):
        u = UserFactory(is_staff=True)
        out = self.call_command()
        self.assertTrue(u.username in out)

    def test_does_not_include_non_staff(self):
        u = UserFactory(is_staff=False)
        out = self.call_command()
        self.assertFalse(u.username in out)

    def test_only_includes_active_staff(self):
        """we don't care about inactive users"""
        u_active = UserFactory(is_staff=True, is_active=True)
        u_inactive = UserFactory(is_staff=True, is_active=False)

        out = self.call_command()

        self.assertTrue(u_active.username in out)
        self.assertFalse(
            u_inactive.username in out, "inactive staff should not be listed"
        )

    def test_alphabetical_order(self):
        # create them in non-alphabetical order
        UserFactory(username="b_user", is_staff=True),
        UserFactory(username="c_user", is_staff=True),
        UserFactory(username="a_user", is_staff=True),

        out = self.call_command()

        self.assertTrue("a_user\nb_user\nc_user" in out)
