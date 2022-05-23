from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.utils import json

from djangoldp.tests.models import Conversation, Project, Circle, CircleMember, User


class TestCache(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com',
                                                         password='glass onion', first_name='John')
        self.client.force_authenticate(self.user)

    def tearDown(self):
        setattr(Circle._meta, 'depth', 0)
        setattr(Circle._meta, 'empty_containers', [])

    # test container cache after new resource added
    @override_settings(SERIALIZER_CACHE=True)
    def test_save_fk_graph_with_nested(self):
        response = self.client.get('/batchs/', content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        post = {
            '@graph': [
                {
                    'http://happy-dev.fr/owl/#title': "title",
                    'http://happy-dev.fr/owl/#invoice': {
                        '@id': "_.123"
                    }
                },
                {
                    '@id': "_.123",
                    'http://happy-dev.fr/owl/#title': "title 2"
                }
            ]
        }

        response = self.client.post('/batchs/', data=json.dumps(post), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/batchs/', content_type='application/ld+json')
        self.assertIn('ldp:contains', response.data)
        self.assertEquals(response.data['ldp:contains'][0]['title'], "title")
        self.assertEquals(response.data['ldp:contains'][0]['invoice']['title'], "title 2")

    # test resource cache after it is updated
    @override_settings(SERIALIZER_CACHE=True)
    def test_update_with_new_fk_relation(self):
        conversation = Conversation.objects.create(author_user=self.user, description="conversation description")
        response = self.client.get('/conversations/{}/'.format(conversation.pk), content_type='application/ld+json')
        body = [
            {
                '@id': "/conversations/{}/".format(conversation.pk),
                'http://happy-dev.fr/owl/#description': "conversation update",
                'http://happy-dev.fr/owl/#peer_user': {
                    '@id': self.user.urlid,
                }
            }
        ]
        response = self.client.put('/conversations/{}/'.format(conversation.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/conversations/{}/'.format(conversation.pk), content_type='application/ld+json')
        self.assertIn('peer_user', response.data)
        self.assertEquals('conversation update', response.data['description'])
        self.assertEqual(response.data['peer_user']['@id'], self.user.urlid)
        self.assertIn('@type', response.data['peer_user'])

    # test resource cache after it is updated - external resource
    @override_settings(SERIALIZER_CACHE=True)
    def test_update_with_new_fk_relation_external(self):
        conversation = Conversation.objects.create(author_user=self.user, description="conversation description")
        response = self.client.get('/conversations/{}/'.format(conversation.pk), content_type='application/ld+json')
        external_user = get_user_model().objects.create_user(username='external', email='jlennon@beatles.com',
                                                             password='glass onion', urlid='https://external.com/users/external/')
        body = [
            {
                '@id': "/conversations/{}/".format(conversation.pk),
                'http://happy-dev.fr/owl/#description': "conversation update",
                'http://happy-dev.fr/owl/#peer_user': {
                    '@id': external_user.urlid,
                }
            }
        ]
        response = self.client.put('/conversations/{}/'.format(conversation.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/conversations/{}/'.format(conversation.pk), content_type='application/ld+json')
        self.assertIn('peer_user', response.data)
        self.assertEquals('conversation update', response.data['description'])
        self.assertIn('@id', response.data['peer_user'])
        # serialize external id and only external id
        self.assertEqual(response.data['peer_user']['@id'], external_user.urlid)
        self.assertIn('@type', response.data['peer_user'])
        self.assertEqual(len(response.data['peer_user']), 2)

    # test container cache after member is deleted by view
    @override_settings(SERIALIZER_CACHE=True)
    def test_cached_container_deleted_resource_view(self):
        conversation = Conversation.objects.create(author_user=self.user, description="conversation description")
        response = self.client.get('/conversations/', content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

        response = self.client.delete('/conversations/{}/'.format(conversation.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/conversations/', content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

    # test container cache after member is deleted manually
    @override_settings(SERIALIZER_CACHE=True)
    def test_cached_container_deleted_resource_manual(self):
        conversation = Conversation.objects.create(author_user=self.user, description="conversation description")
        response = self.client.get('/conversations/', content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

        conversation.delete()

        response = self.client.get('/conversations/', content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

    # test resource cache after it is deleted manually
    @override_settings(SERIALIZER_CACHE=True)
    def test_cached_resource_deleted_resource_manual(self):
        conversation = Conversation.objects.create(author_user=self.user, description="conversation description")
        response = self.client.get('/conversations/{}/'.format(conversation.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        conversation.delete()

        response = self.client.get('/conversations/{}/'.format(conversation.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # test container cache following m2m_changed - Project (which inherits from djangoldp.models.Model)
    @override_settings(SERIALIZER_CACHE=True)
    def test_cached_container_m2m_changed_project(self):
        project = Project.objects.create(description='Test')
        response = self.client.get('/projects/{}/members/'.format(project.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

        project.members.add(self.user)
        response = self.client.get('/projects/{}/members/'.format(project.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

        project.members.remove(self.user)
        response = self.client.get('/projects/{}/members/'.format(project.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

        project.members.add(self.user)
        project.members.clear()
        response = self.client.get('/projects/{}/members/'.format(project.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

    # test container cache following m2m_changed - Conversation (which does not inherit from djangoldp.models.Model)
    @override_settings(SERIALIZER_CACHE=True)
    def test_cached_container_m2m_changed_conversation(self):
        conversation = Conversation.objects.create(author_user=self.user, description="conversation description")
        response = self.client.get('/conversations/{}/observers/'.format(conversation.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

        conversation.observers.add(self.user)
        response = self.client.get('/conversations/{}/observers/'.format(conversation.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

        conversation.observers.remove(self.user)
        response = self.client.get('/conversations/{}/observers/'.format(conversation.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

        conversation.observers.add(self.user)
        conversation.observers.clear()
        response = self.client.get('/conversations/{}/observers/'.format(conversation.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 0)

    # test cache working inside of the nested field (serializer) of another object
    @override_settings(SERIALIZER_CACHE=True)
    def test_cached_container_serializer_nested_field(self):
        project = Project.objects.create(description='Test')
        response = self.client.get('/projects/{}/'.format(project.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['members']['ldp:contains']), 0)

        project.members.add(self.user)
        response = self.client.get('/projects/{}/'.format(project.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['members']['ldp:contains']), 1)

        project.members.remove(self.user)
        response = self.client.get('/projects/{}/'.format(project.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['members']['ldp:contains']), 0)

        project.members.add(self.user)
        project.members.clear()
        response = self.client.get('/projects/{}/'.format(project.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['members']['ldp:contains']), 0)

    # test cache working on a serialized nested field at higher depth
    @override_settings(SERIALIZER_CACHE=True)
    def test_cache_depth_2(self):
        setattr(Circle._meta, 'depth', 2)

        circle = Circle.objects.create(description='Test')
        response = self.client.get('/circles/{}/'.format(circle.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['members']['ldp:contains']), 0)

        CircleMember.objects.create(user=self.user, circle=circle)
        response = self.client.get('/circles/{}/'.format(circle.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['members']['ldp:contains']), 1)
        # assert the depth is applied
        self.assertIn('user', response.data['members']['ldp:contains'][0])
        self.assertIn('first_name', response.data['members']['ldp:contains'][0]['user'])
        self.assertEqual(response.data['members']['ldp:contains'][0]['user']['first_name'], self.user.first_name)

        # make a change to the _user_
        self.user.first_name = "Alan"
        self.user.save()

        # assert that the use under the circles members has been updated
        response = self.client.get('/circles/{}/'.format(circle.pk), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['members']['ldp:contains']), 1)
        self.assertIn('user', response.data['members']['ldp:contains'][0])
        self.assertIn('first_name', response.data['members']['ldp:contains'][0]['user'])
        self.assertEqual(response.data['members']['ldp:contains'][0]['user']['first_name'], self.user.first_name)

    # test the cache behaviour when empty_containers is an active setting
    @override_settings(SERIALIZER_CACHE=True)
    def test_cache_empty_container(self):
        setattr(Circle._meta, 'depth', 1)
        setattr(Circle._meta, 'empty_containers', ['members'])

        circle = Circle.objects.create(name='test', description='test')
        CircleMember.objects.create(user=self.user, circle=circle)

        # make one call on the parent
        response = self.client.get('/circles/', content_type='application/ld+json')
        self.assertEqual(response.data['@type'], 'ldp:Container')
        self.assertIn('members', response.data['ldp:contains'][0])
        self.assertIn('@id', response.data['ldp:contains'][0]['members'])
        self.assertNotIn('@type', response.data['ldp:contains'][0]['members'])
        self.assertNotIn('permissions', response.data['ldp:contains'][0]['members'])
        self.assertNotIn('ldp:contains', response.data['ldp:contains'][0]['members'])

        # and a second on the child
        response = self.client.get('/circles/1/members/', content_type='application/ld+json')
        self.assertEqual(response.data['@type'], 'ldp:Container')
        self.assertIn('@id', response.data)
        self.assertIn('ldp:contains', response.data)
        self.assertIn('permissions', response.data)
        self.assertIn('circle', response.data['ldp:contains'][0])
