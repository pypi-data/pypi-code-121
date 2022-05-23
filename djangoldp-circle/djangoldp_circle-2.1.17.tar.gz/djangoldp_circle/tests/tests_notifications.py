import uuid
import json
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from guardian.shortcuts import assign_perm

from djangoldp.models import Activity
from djangoldp_circle.models import Circle, CircleMember, CircleAccessRequest, manage_deleted_owner
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
    
    def test_circle_access_request_changes_trigger_notifications(self):
        from djangoldp_notification.models import Notification

        # test that the creation of a CircleAccessRequest triggers the sending of notifications to admins of a circle
        creator = get_random_user()
        second_admin = get_random_user()
        distant_admin = get_random_user()
        distant_admin.urlid = "https://distantserver.com/users/1/"
        distant_admin.save()
        self.setUpCircle('Restricted', owner=creator)
        CircleMember.objects.create(user=second_admin, circle=self.circle, is_admin=True)
        CircleMember.objects.create(user=distant_admin, circle=self.circle, is_admin=True)

        self.setUpLoggedInUser()
        ar = CircleAccessRequest.objects.create(user=self.user, circle=self.circle)

        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(creator.inbox.count(), 1)
        self.assertEqual(second_admin.inbox.count(), 1)
        self.assertEqual(Activity.objects.count(), 1)

        # test that responding to the request triggers another
        ar.status = "Accepted"
        ar.responded_to_by = creator
        ar.save()

        self.assertEqual(Notification.objects.count(), 3)
        self.assertEqual(self.user.inbox.count(), 1)
