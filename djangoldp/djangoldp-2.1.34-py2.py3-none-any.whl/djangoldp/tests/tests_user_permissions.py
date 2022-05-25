from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.conf import settings
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase
from djangoldp.tests.models import JobOffer, LDPDummy, PermissionlessDummy, UserProfile, OwnedResource, \
    NoSuperUsersAllowedModel, ComplexPermissionClassesModel

import json


class TestUserPermissions(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com', password='glass onion')
        self.client = APIClient(enforce_csrf_checks=True)
        self.client.force_authenticate(user=self.user)
        self.job = JobOffer.objects.create(title="job", slug="slug1")

    def setUpGroup(self):
        self.group = Group.objects.create(name='Test')
        view_perm = Permission.objects.get(codename='view_permissionlessdummy')
        self.group.permissions.add(view_perm)
        self.group.save()

    def _make_self_superuser(self):
        self.user.is_superuser = True
        self.user.save()

    # list - simple
    @override_settings(SERIALIZE_EXCLUDE_PERMISSIONS=['inherit'],
                       SERIALIZE_CONTAINER_EXCLUDE_PERMISSIONS=['inherit', 'delete'])
    def test_get_for_authenticated_user(self):
        response = self.client.get('/job-offers/')
        self.assertEqual(response.status_code, 200)
        # test serialized permissions
        self.assertIn({'mode': {'@type': 'view'}}, response.data['permissions'])
        self.assertNotIn({'mode': {'@type': 'inherit'}}, response.data['permissions'])
        # self.assertNotIn({'mode': {'@type': 'delete'}}, response.data['permissions'])

    # TODO: list - I do not have permission from the model, but I do have permission via a Group I am assigned
    #  https://git.startinblox.com/djangoldp-packages/djangoldp/issues/291
    '''def test_group_list_access(self):
        self.setUpGroup()
        dummy = PermissionlessDummy.objects.create()

        response = self.client.get('/permissionless-dummys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

        LDListMixin.to_representation_cache.reset()
        LDPSerializer.to_representation_cache.reset()

        self.user.groups.add(self.group)
        self.user.save()
        response = self.client.get('/permissionless-dummys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # repeat of the above test on nested field
    def test_group_list_access_nested_field(self):
        self.setUpGroup()
        parent = LDPDummy.objects.create()
        PermissionlessDummy.objects.create(parent=parent)

        response = self.client.get('/ldpdummys/{}/'.format(parent.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['anons']['ldp:contains']), 0)

        LDListMixin.to_representation_cache.reset()
        LDPSerializer.to_representation_cache.reset()

        self.user.groups.add(self.group)
        self.user.save()
        response = self.client.get('/ldpdummys/{}/'.format(parent.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['anons']['ldp:contains']), 1)

    # repeat of the test on a nested viewset
    def test_group_list_access_nested_viewset(self):
        self.setUpGroup()
        parent = LDPDummy.objects.create()
        PermissionlessDummy.objects.create(parent=parent)

        response = self.client.get('/ldpdummys/{}/anons/'.format(parent.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

        LDListMixin.to_representation_cache.reset()
        LDPSerializer.to_representation_cache.reset()

        self.user.groups.add(self.group)
        self.user.save()
        response = self.client.get('/ldpdummys/{}/anons/'.format(parent.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # repeat for object-specific request
    def test_group_object_access(self):
        self.setUpGroup()
        dummy = PermissionlessDummy.objects.create()

        response = self.client.get('/permissionless-dummys/{}'.format(dummy))
        self.assertEqual(response.status_code, 404)

        LDListMixin.to_representation_cache.reset()
        LDPSerializer.to_representation_cache.reset()

        self.user.groups.add(self.group)
        self.user.save()
        response = self.client.get('/permissionless-dummys/{}/'.format(dummy))
        self.assertEqual(response.status_code, 200)
    
    # TODO: test for POST scenario
    # TODO: test for PUT scenario
    # TODO: test for DELETE scenario   
    '''

    @override_settings(SERIALIZE_OBJECT_EXCLUDE_PERMISSIONS=['inherit'])
    def test_get_1_for_authenticated_user(self):
        response = self.client.get('/job-offers/{}/'.format(self.job.slug))
        self.assertEqual(response.status_code, 200)
        self.assertIn({'mode': {'@type': 'view'}}, response.data['permissions'])
        self.assertNotIn({'mode': {'@type': 'inherit'}}, response.data['permissions'])

    def test_post_request_for_authenticated_user(self):
        post = {'http://happy-dev.fr/owl/#title': "job_created", "http://happy-dev.fr/owl/#slug": 'slug2'}
        response = self.client.post('/job-offers/', data=json.dumps(post), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # denied because I don't have model permissions
    def test_post_request_denied_model_perms(self):
        data = {'http://happy-dev.fr/owl/#some': 'title'}
        response = self.client.post('/permissionless-dummys/', data=json.dumps(data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_post_nested_view_authorized(self):
        data = { "http://happy-dev.fr/owl/#title": "new skill", "http://happy-dev.fr/owl/#obligatoire": "okay" }
        response = self.client.post('/job-offers/{}/skills/'.format(self.job.slug), data=json.dumps(data),
                                    content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    def test_post_nested_view_denied_model_perms(self):
        parent = LDPDummy.objects.create(some='parent')
        data = { "http://happy-dev.fr/owl/#some": "title" }
        response = self.client.post('/ldpdummys/{}/anons/'.format(parent.pk), data=json.dumps(data),
                                    content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_put_request_for_authenticated_user(self):
        body = {'https://happy-dev.fr/owl/#title':"job_updated"}
        response = self.client.put('/job-offers/{}/'.format(self.job.slug), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

    def test_request_patch_for_authenticated_user(self):
        response = self.client.patch('/job-offers/' + str(self.job.slug) + "/",
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

    def test_put_request_denied_model_perms(self):
        dummy = PermissionlessDummy.objects.create(some='some', slug='slug')
        data = {'http://happy-dev.fr/owl/#some': 'new'}
        response = self.client.put('/permissionless-dummys/{}/'.format(dummy.slug), data=json.dumps(data),
                                    content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    def test_put_nested_view_denied_model_perms(self):
        parent = LDPDummy.objects.create(some='parent')
        child = PermissionlessDummy.objects.create(some='child', slug='child', parent=parent)
        data = {"http://happy-dev.fr/owl/#some": "new"}
        response = self.client.put('/ldpdummys/{}/anons/{}/'.format(parent.pk, child.slug), data=json.dumps(data),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    def test_patch_nested_container_attach_existing_resource_permission_denied(self):
        '''I am attempting to add a resource which I should not know exists'''
        parent = LDPDummy.objects.create(some='parent')
        dummy = PermissionlessDummy.objects.create(some='some', slug='slug')
        data = {
            'http://happy-dev.fr/owl/#anons': [
                {'@id': '{}/permissionless-dummys/{}/'.format(settings.SITE_URL, dummy.slug), 'http://happy-dev.fr/owl/#slug': dummy.slug}
            ]
        }
        response = self.client.patch('/ldpdummys/{}/'.format(parent.pk), data=json.dumps(data), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # variations on previous tests with an extra level of depth
    # TODO
    def test_post_nested_container_twice_nested_permission_denied(self):
        pass

    # TODO
    def test_put_nested_container_twice_nested_permission_denied(self):
        pass

    # TODO: repeat of the above where it is authorized because I have permission through my Group
    #  https://git.startinblox.com/djangoldp-packages/djangoldp/issues/291

    def test_put_request_change_urlid_rejected(self):
        self.assertEqual(JobOffer.objects.count(), 1)
        body = {'@id': "ishouldnotbeabletochangethis"}
        response = self.client.put('/job-offers/{}/'.format(self.job.slug), data=json.dumps(body),
                                   content_type='application/ld+json')
        # TODO: this is failing quietly
        #  https://git.happy-dev.fr/startinblox/solid-spec/issues/14
        self.assertEqual(response.status_code, 200)
        self.assertEqual(JobOffer.objects.count(), 1)
        self.assertFalse(JobOffer.objects.filter(urlid=body['@id']).exists())

    def test_put_request_change_pk_rejected(self):
        self.assertEqual(JobOffer.objects.count(), 1)
        body = {'http://happy-dev.fr/owl/#pk': 2}
        response = self.client.put('/job-offers/{}/'.format(self.job.slug), data=json.dumps(body),
                                   content_type='application/ld+json')
        # TODO: this is failing quietly
        #  https://git.happy-dev.fr/startinblox/solid-spec/issues/14
        self.assertEqual(response.status_code, 200)
        self.assertEqual(JobOffer.objects.count(), 1)
        self.assertFalse(JobOffer.objects.filter(pk=body['http://happy-dev.fr/owl/#pk']).exists())

    # tests that I receive a list of objects for which I am owner, filtering those for which I am not
    def test_list_owned_resources(self):
        my_resource = OwnedResource.objects.create(description='test', user=self.user)
        another_user = get_user_model().objects.create_user(username='test', email='test@test.com', password='test')
        their_resource = OwnedResource.objects.create(description='another test', user=another_user)

        response = self.client.get('/ownedresources/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)
        self.assertEqual(response.data['ldp:contains'][0]['@id'], my_resource.urlid)

    # I do not have model permissions as an authenticated user, but I am the resources' owner
    def test_get_owned_resource(self):
        my_resource = OwnedResource.objects.create(description='test', user=self.user)
        another_user = get_user_model().objects.create_user(username='test', email='test@test.com', password='test')
        their_resource = OwnedResource.objects.create(description='another test', user=another_user)

        response = self.client.get('/ownedresources/{}/'.format(my_resource.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['@id'], my_resource.urlid)
        self.assertIn({'mode': {'@type': 'delete'}}, response.data['permissions'])

        # I have permission to view this resource
        response = self.client.patch('/ownedresources/{}/'.format(their_resource.pk))
        self.assertEqual(response.status_code, 404)

    def test_patch_owned_resource(self):
        my_profile = UserProfile.objects.create(user=self.user, slug=self.user.username, description='about me')
        another_user = get_user_model().objects.create_user(username='test', email='test@test.com', password='test')
        their_profile = UserProfile.objects.create(user=another_user, slug=another_user.username, description='about')

        response = self.client.patch('/userprofiles/{}/'.format(my_profile.slug))
        self.assertEqual(response.status_code, 200)

        response = self.client.patch('/userprofiles/{}/'.format(their_profile.slug))
        # TODO: technically this should be 403, since I do have permission to view their user profile
        #  https://git.startinblox.com/djangoldp-packages/djangoldp/issues/336
        self.assertEqual(response.status_code, 404)

    def test_delete_owned_resource(self):
        my_resource = OwnedResource.objects.create(description='test', user=self.user)
        another_user = get_user_model().objects.create_user(username='test', email='test@test.com', password='test')
        their_resource = OwnedResource.objects.create(description='another test', user=another_user)

        response = self.client.delete('/ownedresources/{}/'.format(my_resource.pk))
        self.assertEqual(response.status_code, 204)

        response = self.client.delete('/ownedresources/{}/'.format(their_resource.pk))
        self.assertEqual(response.status_code, 404)

    # test superuser permissions (configured on model)
    def test_list_superuser_perms(self):
        another_user = get_user_model().objects.create_user(username='test', email='test@test.com', password='test')
        their_resource = OwnedResource.objects.create(description='another test', user=another_user)

        response = self.client.get('/ownedresources/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

        # now I'm superuser, I have the permissions
        self._make_self_superuser()

        response = self.client.get('/ownedresources/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    def test_get_superuser_perms(self):
        another_user = get_user_model().objects.create_user(username='test', email='test@test.com', password='test')
        their_resource = OwnedResource.objects.create(description='another test', user=another_user)

        response = self.client.patch('/ownedresources/{}/'.format(their_resource.pk))
        self.assertEqual(response.status_code, 404)

        self._make_self_superuser()

        response = self.client.patch('/ownedresources/{}/'.format(their_resource.pk))
        self.assertEqual(response.status_code, 200)

    def test_put_superuser_perms(self):
        another_user = get_user_model().objects.create_user(username='test', email='test@test.com', password='test')
        their_profile = UserProfile.objects.create(user=another_user, slug=another_user.username, description='about')

        response = self.client.patch('/userprofiles/{}/'.format(their_profile.slug))
        # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/336
        self.assertEqual(response.status_code, 404)

        self._make_self_superuser()

        response = self.client.patch('/userprofiles/{}/'.format(their_profile.slug))
        self.assertEqual(response.status_code, 200)

    def test_delete_superuser_perms(self):
        another_user = get_user_model().objects.create_user(username='test', email='test@test.com', password='test')
        their_resource = OwnedResource.objects.create(description='another test', user=another_user)

        response = self.client.delete('/ownedresources/{}/'.format(their_resource.pk))
        self.assertEqual(response.status_code, 404)

        self._make_self_superuser()

        response = self.client.delete('/ownedresources/{}/'.format(their_resource.pk))
        self.assertEqual(response.status_code, 204)

    # test where superuser_perms are configured on the model to be different
    def test_superuser_perms_configured(self):
        self._make_self_superuser()

        NoSuperUsersAllowedModel.objects.create()
        self.assertEqual(NoSuperUsersAllowedModel.objects.count(), 1)

        response = self.client.get('/nosuperusersallowedmodels/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

    # test list where SuperUserPermission is being used on a model in conjunction with LDPPermissions
    def test_filter_backend_multiple_permission_classes_configured(self):
        ComplexPermissionClassesModel.objects.create()

        response = self.client.get('/complexpermissionclassesmodels/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

    # I have model (or object?) permissions. Attempt to make myself owner and thus upgrade my permissions
    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/356/
    '''
    def test_hack_model_perms_privilege_escalation(self):
        another_user = get_user_model().objects.create_user(username='test', email='test@test.com', password='test')
        resource = OwnedResourceVariant.objects.create(description='another test', user=another_user)

        # authenticated has 'change' permission but only owner's have 'control' permission, meaning that I should
        # not be able to change my privilege level
        body = {
            'http://happy-dev.fr/owl/#user': {'@id': self.user.urlid}
        }
        response = self.client.put('/ownedresourcevariants/{}/'.format(resource.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        resource = OwnedResourceVariant.objects.get(pk=resource.pk)
        self.assertNotEqual(resource.user, self.user)
    '''
