import json
import uuid
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient, APITestCase
from guardian.shortcuts import assign_perm

from .models import PermissionlessDummy, Dummy, LDPDummy


class TestsGuardian(APITestCase):

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def setUpLoggedInUser(self):
        self.user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com',
                                                         password='glass onion')
        self.group = Group.objects.create(name='Test')
        self.user.groups.add(self.group)
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def _get_dummy_with_perms(self, perms=None, parent=None, group=False):
        if perms is None:
            perms = []
        dummy = PermissionlessDummy.objects.create(some='test', slug=uuid.uuid4(), parent=parent)
        model_name = PermissionlessDummy._meta.model_name

        for perm in perms:
            perm = perm + '_' + model_name
            if group:
                assign_perm(perm, self.group, dummy)
            else:
                assign_perm(perm, self.user, dummy)

        return dummy

    # optional setup for testing PermissionlessDummy model with parameterised perms
    def setUpGuardianDummyWithPerms(self, perms=None, parent=None, group=False):
        self.dummy = self._get_dummy_with_perms(perms, parent, group)

    # auxiliary function converts permission format for test
    def _unpack_permissions(self, perms_from_response):
        return [p['mode']['@type'] for p in perms_from_response]

    # test that dummy with no permissions set returns no results
    def test_get_dummy_no_permissions(self):
        self.setUpLoggedInUser()
        self.setUpGuardianDummyWithPerms()
        response = self.client.get('/permissionless-dummys/{}/'.format(self.dummy.slug))
        self.assertEqual(response.status_code, 404)

    # test with anonymous user
    def test_get_dummy_anonymous_user(self):
        self.setUpGuardianDummyWithPerms()
        response = self.client.get('/permissionless-dummys/')
        # I have no object permissions - I should receive a 403
        self.assertEqual(response.status_code, 403)

    def test_list_dummy_exception(self):
        self.setUpLoggedInUser()
        # I have permission on a permissionless dummy, but not in general
        dummy_a = self._get_dummy_with_perms()
        dummy_b = self._get_dummy_with_perms(['view'])
        response = self.client.get('/permissionless-dummys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)
        containees = [d['@id'] for d in response.data['ldp:contains']]
        self.assertNotIn(dummy_a.urlid, containees)
        self.assertIn(dummy_b.urlid, containees)

    def test_list_dummy_group_exception(self):
        self.setUpLoggedInUser()
        dummy_a = self._get_dummy_with_perms()
        dummy_b = self._get_dummy_with_perms(['view'], group=True)
        response = self.client.get('/permissionless-dummys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)
        containees = [d['@id'] for d in response.data['ldp:contains']]
        self.assertNotIn(dummy_a.urlid, containees)
        self.assertIn(dummy_b.urlid, containees)

    def test_list_dummy_exception_nested_view(self):
        self.setUpLoggedInUser()
        parent = LDPDummy.objects.create(some="test")
        # two dummies, one I have permission to view and one I don't
        dummy_a = self._get_dummy_with_perms(parent=parent)
        dummy_b = self._get_dummy_with_perms(['view'], parent)
        response = self.client.get('/ldpdummys/{}/anons/'.format(parent.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    def test_list_dummy_exception_nested_serializer(self):
        self.setUpLoggedInUser()
        parent = LDPDummy.objects.create(some="test")
        # two dummies, one I have permission to view and one I don't
        dummy_a = self._get_dummy_with_perms(parent=parent)
        dummy_b = self._get_dummy_with_perms(['view'], parent)
        response = self.client.get('/ldpdummys/{}/'.format(parent.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['anons']['ldp:contains']), 1)

    def test_get_dummy_permission_granted(self):
        self.setUpLoggedInUser()
        self.setUpGuardianDummyWithPerms(['view'])
        response = self.client.get('/permissionless-dummys/{}/'.format(self.dummy.slug))
        self.assertEqual(response.status_code, 200)

    def test_get_dummy_group_permission_granted(self):
        self.setUpLoggedInUser()
        self.setUpGuardianDummyWithPerms(['view'], group=True)
        response = self.client.get('/permissionless-dummys/{}/'.format(self.dummy.slug))
        self.assertEqual(response.status_code, 200)

    def test_get_dummy_permission_rejected(self):
        self.setUpLoggedInUser()
        self.setUpGuardianDummyWithPerms(['view'])
        dummy_without = PermissionlessDummy.objects.create(some='test2', slug='test2')
        response = self.client.get('/permissionless-dummys/{}/'.format(dummy_without.slug))
        self.assertEqual(response.status_code, 404)

    def test_patch_dummy_permission_granted(self):
        self.setUpLoggedInUser()
        self.setUpGuardianDummyWithPerms(['view', 'change'])
        body = {'some': "some_new"}
        response = self.client.patch('/permissionless-dummys/{}/'.format(self.dummy.slug), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

    def test_patch_dummy_permission_rejected(self):
        self.setUpLoggedInUser()
        self.setUpGuardianDummyWithPerms(['change'])
        dummy_without = PermissionlessDummy.objects.create(some='test2', slug='test2')
        body = {'some': "some_new"}
        response = self.client.patch('/permissionless-dummys/{}/'.format(dummy_without.slug), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # TODO: PUT container of many objects approved on specific resource for which I do not have _model_ permissions

    # test that custom permissions are returned on a model
    def test_custom_permissions(self):
        self.setUpLoggedInUser()
        self.setUpGuardianDummyWithPerms(['custom_permission', 'view'])

        response = self.client.get('/permissionless-dummys/{}/'.format(self.dummy.slug))
        self.assertIn('custom_permission', self._unpack_permissions(response.data['permissions']))

    # test that duplicate permissions aren't returned
    def test_no_duplicate_permissions(self):
        self.setUpLoggedInUser()
        dummy = Dummy.objects.create(some='test', slug='test')
        model_name = Dummy._meta.model_name

        assign_perm('view_' + model_name, self.user, dummy)

        response = self.client.get('/dummys/{}/'.format(dummy.slug))
        self.assertEqual(response.status_code, 200)
        perms = self._unpack_permissions(response.data['permissions'])
        self.assertIn('view', perms)
        view_perms = [perm for perm in perms if perm == 'view']
        self.assertEqual(len(view_perms), 1)

    # TODO: attempting to migrate my object permissions by changing FK reference
