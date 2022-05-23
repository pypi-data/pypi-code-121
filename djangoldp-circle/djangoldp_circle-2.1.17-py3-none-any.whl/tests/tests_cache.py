import uuid
import json
from datetime import datetime, timedelta

from djangoldp.permissions import LDPPermissions

from rest_framework.test import APITestCase, APIClient
from guardian.shortcuts import assign_perm

from djangoldp_circle.models import Circle, CircleMember
from djangoldp_circle.tests.utils import get_random_user


class CacheTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def setUpLoggedInUser(self):
        self.user = get_random_user()
        self.client.force_authenticate(user=self.user)

    def _get_random_circle(self, status_choice='Public', owner=None):
        if owner is None:
            owner = self.user

        return Circle.objects.create(name='Test', status=status_choice, owner=owner)

    def setUpCircle(self, status_choice='Public', owner=None):
        self.circle = self._get_random_circle(status_choice, owner)

    def test_leave_circle_user_cache_updates(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle(owner=another_user)
        me = CircleMember.objects.create(user=self.user, circle=self.circle, is_admin=False)

        response = self.client.get('/users/{}/'.format(self.user.username))
        self.assertEqual(len(response.data['circles']['ldp:contains']), 1)

        response = self.client.delete('/circle-members/{}/'.format(me.pk))
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/users/{}/'.format(self.user.username))
        self.assertEqual(len(response.data['circles']['ldp:contains']), 0)

    # variation where I'm calling it on the container directly
    def test_leave_circle_user_cache_updates_list(self):
        self.setUpLoggedInUser()
        another_user = get_random_user()
        self.setUpCircle(owner=another_user)
        me = CircleMember.objects.create(user=self.user, circle=self.circle, is_admin=False)

        response = self.client.get('/users/{}/circles/'.format(self.user.username))
        self.assertEqual(len(response.data['ldp:contains']), 1)

        response = self.client.delete('/circle-members/{}/'.format(me.pk))
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/users/{}/circles/'.format(self.user.username))
        self.assertEqual(len(response.data['ldp:contains']), 0)
