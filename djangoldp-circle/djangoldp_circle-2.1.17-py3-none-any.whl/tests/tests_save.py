import uuid
import json
from datetime import datetime, timedelta
from rest_framework.test import APITestCase, APIClient
from guardian.shortcuts import assign_perm

from djangoldp_circle.models import Circle, CircleMember, manage_deleted_owner
from djangoldp_circle.tests.utils import get_random_user
from djangoldp_account.models import LDPUser


class SaveTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def setUpLoggedInUser(self):
        self.user = get_random_user()
        self.client.force_authenticate(user=self.user)

    def setUpCircle(self, status_choice='Public', owner=None):
        if owner is None:
            owner = self.user

        self.circle = Circle.objects.create(name='Test', status=status_choice, owner=owner)

    # tests for handling owner removed functionality
    def test_owner_removed_listener_second_admin(self):
        # there is a circle with 2 admins and 3 total users
        self.setUpLoggedInUser()
        self.setUpCircle()
        another_user = get_random_user()
        CircleMember.objects.create(circle=self.circle, user=another_user, is_admin=False)
        admin_user = get_random_user()
        CircleMember.objects.create(circle=self.circle, user=admin_user, is_admin=True)

        # the owner user was deleted - but there is another admin in the circle
        cm = self.circle.members.get(user=self.user)
        manage_deleted_owner('', cm)
        self.user.delete()

        # a new owner should be set as the other admin user
        circle = Circle.objects.get(pk=self.circle.pk)
        self.assertEqual(CircleMember.objects.count(), 2)
        self.assertEqual(circle.owner, admin_user)

    def test_owner_removed_listener_second_member(self):
        # the owner user was deleted - there is no other admin but there is another user
        self.setUpLoggedInUser()
        self.setUpCircle()
        another_user = get_random_user()
        CircleMember.objects.create(circle=self.circle, user=another_user, is_admin=False)

        cm = self.circle.members.get(user=self.user)
        manage_deleted_owner('', cm)
        self.user.delete()

        # a new owner should be set as the other (non-admin) user
        circle = Circle.objects.get(pk=self.circle.pk)
        self.assertEqual(CircleMember.objects.count(), 1)
        self.assertEqual(circle.owner, another_user)

    def test_last_user_in_circle_deleted(self):
        # when the last CircleMember is deleted the circle should be deleted too
        self.setUpLoggedInUser()
        self.setUpCircle()
        self.user.delete()
        self.assertEqual(Circle.objects.count(), 0)

    def test_circle_deleted(self):
        # testing that deleting a CircleMember by deleting the Circle does not cause problems
        self.setUpLoggedInUser()
        self.setUpCircle()
        self.circle.delete()
        self.assertEqual(Circle.objects.count(), 0)
        self.assertEqual(LDPUser.objects.count(), 1)
