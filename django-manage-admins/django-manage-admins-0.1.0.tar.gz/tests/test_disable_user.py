from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from .factories import UserFactory


class TestDisableUser(TestCase):
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "disable_user",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_command_exists(self):
        """just make sure the command even exists"""
        self.call_command("dummy")

    def test_disables_active_user(self):
        u = UserFactory(is_active=True)
        self.call_command(u.username)

        # check that they are no longer active
        r = get_user_model().objects.get(username=u.username)
        self.assertFalse(r.is_active)

    def test_already_inactive_user(self):
        """this should just be a no-op"""
        u = UserFactory(is_active=False)
        self.call_command(u.username)

        # check that they are no longer active
        r = get_user_model().objects.get(username=u.username)
        self.assertFalse(r.is_active)
