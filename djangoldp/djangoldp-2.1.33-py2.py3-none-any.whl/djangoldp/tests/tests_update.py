import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.utils import json

from djangoldp.tests.models import UserProfile, Resource, Invoice, Batch, Task, Skill, JobOffer, Conversation, Project,\
    NotificationSetting


class Update(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com',
                                                         password='glass onion')
        self.client.force_authenticate(user=self.user)

    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/326
    '''
    def test_update_container_append_resource(self):
        pre_existing_skill_a = Skill.objects.create(title="to keep", obligatoire="obligatoire", slug="slug1")
        pre_existing_skill_b = Skill.objects.create(title="to keep", obligatoire="obligatoire", slug="slug2")
        job = JobOffer.objects.create(title="job test")
        job.skills.add(pre_existing_skill_a)
        job.skills.add(pre_existing_skill_b)

        post = {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, job.slug),
                "skills": {
                    "ldp:contains": [
                        {"title": "new skill", "obligatoire": "okay"},
                        {"@id": "{}/skills/{}/".format(settings.BASE_URL, pre_existing_skill_b.slug), "title": "z"},
                    ]}
                }

        response = self.client.patch('/job-offers/{}/'.format(job.slug),
                                     data=json.dumps(post),
                                     content_type='application/ld+json')
        self.assertEquals(response.status_code, 200)

        self.assertEquals(response.data['title'], job.title)
        self.assertIs(job.skills.count(), 3)
        skills = job.skills.all().order_by('title')
        self.assertEquals(skills[0].title, "new skill")  # new skill
        self.assertEquals(skills[1].title, pre_existing_skill_a.title)  # old skill unchanged
        self.assertEquals(skills[2].title, "z")  # updated
        self.assertEquals(skills[2].obligatoire, pre_existing_skill_b.obligatoire)  # another field not updated
    '''

    def test_put_resource(self):
        skill = Skill.objects.create(title='original', obligatoire='original', slug='skill1')
        body = [{
            '@id': '{}/skills/{}/'.format(settings.BASE_URL, skill.slug),
            'http://happy-dev.fr/owl/#title': "new", 'http://happy-dev.fr/owl/#obligatoire': "new"}]
        response = self.client.put('/skills/{}/'.format(skill.slug), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['title'], "new")
        self.assertEquals(response.data['obligatoire'], "new")
        self.assertIn('location', response._headers)

    def test_patch_resource(self):
        skill = Skill.objects.create(title='original', obligatoire='original', slug='skill1')
        body = {
            '@id': '{}/skills/{}'.format(settings.BASE_URL, skill.slug),
            'http://happy-dev.fr/owl/#title': 'new'
        }
        response = self.client.patch('/skills/{}/'.format(skill.slug), data=json.dumps(body),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['title'], "new")
        self.assertEquals(response.data['obligatoire'], "original")

    def test_create_sub_object_in_existing_object_with_existing_reverse_1to1_relation(self):
        user = get_user_model().objects.create(username="alex", password="test")
        profile = UserProfile.objects.create(user=user, description="user description")
        body = [
            {
                '@id': "/userprofiles/{}/".format(profile.pk),
                'http://happy-dev.fr/owl/#description': "user update"
            },
            {
                '@id': '/users/{}/'.format(user.pk),
                "http://happy-dev.fr/owl/#first_name": "Alexandre",
                "http://happy-dev.fr/owl/#last_name": "Bourlier",
                "http://happy-dev.fr/owl/#username": "alex",
                'http://happy-dev.fr/owl/#userprofile': {'@id': "/userprofiles/{}/".format(profile.pk)}
            }
        ]
        response = self.client.put('/users/{}/'.format(user.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('userprofile', response.data)

    def test_put_nonexistent_local_resource(self):
        job = JobOffer.objects.create(title="job test")

        # contains internal urlid which refers to non-existent resource
        body = {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, job.slug),
                "skills": {
                    "ldp:contains": [
                        {"@id": "{}/skills/404/".format(settings.BASE_URL)},
                    ]}
                }

        response = self.client.put('/job-offers/{}/'.format(job.slug), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Skill.objects.count(), 0)

    def test_create_sub_object_in_existing_object_with_reverse_fk_relation(self):
        """
        Doesn't work with depth = 0 on UserProfile Model. Should it be ?
        """
        user = get_user_model().objects.create(username="alex", password="test")
        body = [
            {
                '@id': "_:b975",
                'http://happy-dev.fr/owl/#description': "conversation description"
            },
            {
                '@id': '/users/{}/'.format(user.pk),
                "http://happy-dev.fr/owl/#first_name": "Alexandre",
                "http://happy-dev.fr/owl/#last_name": "Bourlier",
                "http://happy-dev.fr/owl/#username": "alex",
                'http://happy-dev.fr/owl/#conversation_set': {'@id': "_:b975"}
            }
        ]
        response = self.client.put('/users/{}/'.format(user.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('conversation_set', response.data)

    def test_create_sub_object_in_existing_object_with_existing_reverse_fk_relation(self):
        user = get_user_model().objects.create(username="alex", password="test")
        conversation = Conversation.objects.create(author_user=user, description="conversation description")
        body = [
            {
                '@id': "/conversations/{}/".format(conversation.pk),
                'http://happy-dev.fr/owl/#description': "conversation update"
            },
            {
                '@id': '/users/{}/'.format(user.pk),
                "http://happy-dev.fr/owl/#first_name": "Alexandre",
                "http://happy-dev.fr/owl/#last_name": "Bourlier",
                "http://happy-dev.fr/owl/#username": "alex",
                'http://happy-dev.fr/owl/#conversation_set': {'@id': "/conversations/{}/".format(conversation.pk)}
            }
        ]
        response = self.client.put('/users/{}/'.format(user.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('conversation_set', response.data)

    def test_missing_field_should_not_be_removed_with_fk_relation(self):
        peer = get_user_model().objects.create(username="sylvain", password="test2")
        conversation = Conversation.objects.create(author_user=self.user, peer_user=peer,
                                                   description="conversation description")
        body = [
            {
                '@id': "/conversations/{}/".format(conversation.pk),
                'http://happy-dev.fr/owl/#description': "conversation update",
            }
        ]
        response = self.client.put('/conversations/{}/'.format(conversation.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('peer_user', response.data)

    def test_empty_field_should_be_removed_with_fk_relation(self):
        peer = get_user_model().objects.create(username="sylvain", password="test2")
        conversation = Conversation.objects.create(author_user=self.user, peer_user=peer,
                                                   description="conversation description")
        body = [
            {
                '@id': "/conversations/{}/".format(conversation.pk),
                'http://happy-dev.fr/owl/#description': "conversation update",
                'http://happy-dev.fr/owl/#peer_user': ""
            }
        ]
        response = self.client.put('/conversations/{}/'.format(conversation.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['peer_user'], None)

    def test_m2m_new_link_bis(self):
        resource = Resource.objects.create()
        job = JobOffer.objects.create(title="first title", slug="job")
        body = {
            'http://happy-dev.fr/owl/#joboffers':
                {
                    '@id': "{}/resources/{}/joboffers/".format(settings.BASE_URL, resource.pk),
                    'ldp:contains': [
                        {'@id': job.urlid,
                         'http://happy-dev.fr/owl/#title': "new job",
                         },
                    ]
                }
        }

        response = self.client.put('/resources/{}/'.format(resource.pk),
                                   data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['joboffers']['ldp:contains'][0]['@id'], job.urlid)
        self.assertEqual(response.data['joboffers']['ldp:contains'][0]['title'], "new job")

    def test_m2m_new_link_embedded(self):
        resource = Resource.objects.create()
        body = {
            'http://happy-dev.fr/owl/#joboffers': {
                'http://happy-dev.fr/owl/#slug': 'aaa',
                'http://happy-dev.fr/owl/#title': "new job",
            }
        }

        response = self.client.put('/resources/{}/'.format(resource.pk),
                                   data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['joboffers']['ldp:contains'][0]['@id'],
                         "http://happy-dev.fr/job-offers/aaa/")
        self.assertEqual(response.data['joboffers']['ldp:contains'][0]['title'], "new job")

    def test_m2m_existing_link(self):
        resource = Resource.objects.create()
        job = JobOffer.objects.create(title="first title", slug="job")
        resource.joboffers.add(job)
        resource.save()
        body = {
            'http://happy-dev.fr/owl/#joboffers': {
                # '@id': "http://testserver/resources/{}/joboffers/".format(resource.pk),
                'ldp:contains': [
                    {
                        '@id': job.urlid,
                        'http://happy-dev.fr/owl/#title': "new job",
                    }
                ]
            }
        }

        response = self.client.put('/resources/{}/'.format(resource.pk),
                                   data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['joboffers']['ldp:contains'][0]['@id'], job.urlid)
        self.assertEqual(response.data['joboffers']['ldp:contains'][0]['title'], "new job")

    def test_m2m_new_link_external(self):
        resource = Resource.objects.create()
        body = {
            'http://happy-dev.fr/owl/#joboffers': {
                'http://happy-dev.fr/owl/#@id': 'http://external.job/job/1',
            }
        }

        response = self.client.put('/resources/{}/'.format(resource.pk),
                                   data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['joboffers']['ldp:contains'][0]['@id'],
                         "http://external.job/job/1")
        self.assertIn('@type', response.data['joboffers']['ldp:contains'][0])

    def test_m2m_new_link_local(self):
        resource = Resource.objects.create()
        job = JobOffer.objects.create(title="first title", slug="job")
        body = {
            'http://happy-dev.fr/owl/#joboffers': {
                '@id': 'http://happy-dev.fr/job-offers/{}/'.format(job.slug),
            }
        }

        response = self.client.put('/resources/{}/'.format(resource.pk),
                                   data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['joboffers']['ldp:contains'][0]['@id'],
                         "http://happy-dev.fr/job-offers/{}/".format(job.slug))
        self.assertEqual(response.data['joboffers']['ldp:contains'][0]['title'], "first title")

    def test_update_with_new_fk_relation(self):
        conversation = Conversation.objects.create(author_user=self.user,
                                                   description="conversation description")
        body = [
            {
                '@id': "/conversations/{}/".format(conversation.pk),
                'http://happy-dev.fr/owl/#description': "conversation update",
                'http://happy-dev.fr/owl/#peer_user': {
                    '@id': 'http://happy-dev.fr/users/{}'.format(self.user.pk),
                }
            }
        ]
        response = self.client.put('/conversations/{}/'.format(conversation.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('peer_user', response.data)

        conversation = Conversation.objects.get(pk=conversation.pk)
        self.assertIsNotNone(conversation.peer_user)

        user = get_user_model().objects.get(pk=self.user.pk)
        self.assertEqual(user.peers_conv.count(), 1)

    def test_m2m_user_link_federated(self):
        project = Project.objects.create(description="project name")
        body = {
            'http://happy-dev.fr/owl/#description': 'project name',
            'http://happy-dev.fr/owl/#members': {
                'http://happy-dev.fr/owl/#@id': 'http://external.user/user/1',
            }
        }

        response = self.client.put('/projects/{}/'.format(project.pk),
                                   data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['members']['ldp:contains'][0]['@id'],
                         "http://external.user/user/1")
        self.assertIn('@type', response.data['members']['ldp:contains'][0])
        self.assertEqual(len(response.data['members']['ldp:contains'][0].items()), 2)

    def test_m2m_user_link_existing_external(self):
        project = Project.objects.create(description="project name")
        ext_user = get_user_model().objects.create(username=str(uuid.uuid4()), urlid='http://external.user/user/1')
        body = {
            'http://happy-dev.fr/owl/#description': 'project name',
            'http://happy-dev.fr/owl/#members': {
                'http://happy-dev.fr/owl/#@id': ext_user.urlid,
            }
        }

        response = self.client.put('/projects/{}/'.format(project.pk),
                                   data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['members']['ldp:contains'][0]['@id'], ext_user.urlid)
        self.assertIn('@type', response.data['members']['ldp:contains'][0])
        self.assertEqual(len(response.data['members']['ldp:contains'][0].items()), 2)

        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.members.count(), 1)

        user = get_user_model().objects.get(pk=ext_user.pk)
        self.assertEqual(user.projects.count(), 1)

    def test_create_sub_object_in_existing_object_with_reverse_1to1_relation(self):
        """
        Doesn't work with depth = 0 on UserProfile Model. Should it be ?
        """
        user = get_user_model().objects.create(username="alex", password="test")
        body = [
            {
                '@id': "_:b975",
                'http://happy-dev.fr/owl/#description': "user description",
                'http://happy-dev.fr/owl/#dummy': {
                    '@id': './'
                }
            },
            {
                '@id': '/users/{}/'.format(user.pk),
                "http://happy-dev.fr/owl/#first_name": "Alexandre",
                "http://happy-dev.fr/owl/#last_name": "Bourlier",
                "http://happy-dev.fr/owl/#username": "alex",
                'http://happy-dev.fr/owl/#userprofile': {'@id': "_:b975"}
            }
        ]
        response = self.client.put('/users/{}/'.format(user.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('userprofile', response.data)
        self.assertIsNotNone(response.data['userprofile'])

    def test_m2m_user_link_remove_existing_link(self):
        ext_user = get_user_model().objects.create(username=str(uuid.uuid4()), urlid='http://external.user/user/1')
        project = Project.objects.create(description="project name")
        project.members.add(ext_user)
        project.save()
        body = {
            'http://happy-dev.fr/owl/#description': 'project name',
            'http://happy-dev.fr/owl/#members': {
            }
        }

        response = self.client.put('/projects/{}/'.format(project.pk),
                                   data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.members.count(), 0)

        user = get_user_model().objects.get(pk=ext_user.pk)
        self.assertEqual(user.projects.count(), 0)

    def test_update_sub_object_with_urlid(self):
        user = get_user_model().objects.create(username="alex", password="test")
        profile = UserProfile.objects.create(user=user, description="user description")
        body = {
            '@id': '/users/{}/'.format(user.pk),
            "first_name": "Alexandre",
            "last_name": "Bourlier",
            "username": "alex",
            'userprofile': {
                '@id': profile.urlid,
                'description': "user update"
            },
            '@context': {
                "@vocab": "http://happy-dev.fr/owl/#",
            }
        }

        response = self.client.put('/users/{}/'.format(user.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('userprofile', response.data)

        response = self.client.get('/userprofiles/{}/'.format(profile.pk),
                                   content_type='application/ld+json')
        self.assertEqual(response.data['description'], "user update")

    # unit tests for a specific bug: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/307
    def test_direct_boolean_field(self):
        profile = UserProfile.objects.create(user=self.user)
        setting = NotificationSetting.objects.create(user=profile, receiveMail=False)
        body = {
            'http://happy-dev.fr/owl/#@id': setting.urlid,
            'receiveMail': True,
            "@context": {"@vocab": "http://happy-dev.fr/owl/#",
                         "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                         "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "ldp": "http://www.w3.org/ns/ldp#",
                         "foaf": "http://xmlns.com/foaf/0.1/", "name": "rdfs:label",
                         "acl": "http://www.w3.org/ns/auth/acl#", "permissions": "acl:accessControl",
                         "mode": "acl:mode", "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#", "lat": "geo:lat",
                         "lng": "geo:long"}
        }

        response = self.client.patch('/notificationsettings/{}/'.format(setting.pk),
                                     data=json.dumps(body),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['receiveMail'], True)

    def test_nested_container_boolean_field_no_slug(self):
        profile = UserProfile.objects.create(user=self.user)
        setting = NotificationSetting.objects.create(user=profile, receiveMail=False)
        body = {
            'settings': {
                'http://happy-dev.fr/owl/#@id': setting.urlid,
                'receiveMail': True
            },
            "@context": {"@vocab": "http://happy-dev.fr/owl/#",
                         "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                         "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "ldp": "http://www.w3.org/ns/ldp#",
                         "foaf": "http://xmlns.com/foaf/0.1/", "name": "rdfs:label",
                         "acl": "http://www.w3.org/ns/auth/acl#", "permissions": "acl:accessControl",
                         "mode": "acl:mode", "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#", "lat": "geo:lat",
                         "lng": "geo:long"}
        }

        response = self.client.patch('/userprofiles/{}/'.format(profile.slug),
                                     data=json.dumps(body),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['settings']['receiveMail'], True)

    # variation where the lookup_field for NotificationSetting (pk) is provided
    def test_nested_container_boolean_field_with_slug(self):
        profile = UserProfile.objects.create(user=self.user)
        setting = NotificationSetting.objects.create(user=profile, receiveMail=False)
        body = {
            'settings': {
                'pk': setting.pk,
                'http://happy-dev.fr/owl/#@id': setting.urlid,
                'receiveMail': True
            },
            "@context": {"@vocab": "http://happy-dev.fr/owl/#",
                         "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                         "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "ldp": "http://www.w3.org/ns/ldp#",
                         "foaf": "http://xmlns.com/foaf/0.1/", "name": "rdfs:label",
                         "acl": "http://www.w3.org/ns/auth/acl#", "permissions": "acl:accessControl",
                         "mode": "acl:mode", "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#", "lat": "geo:lat",
                         "lng": "geo:long"}
        }

        response = self.client.patch('/userprofiles/{}/'.format(profile.slug),
                                     data=json.dumps(body),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['settings']['receiveMail'], True)

    def test_update_container_twice_nested_view(self):
        invoice = Invoice.objects.create(title='test')
        pre_existing_batch = Batch.objects.create(title='batch1', invoice=invoice)
        pre_existing_task = Task.objects.create(title='task1', batch=pre_existing_batch)

        base_url = settings.BASE_URL

        body = {
            "@id": "{}/invoices/{}/".format(base_url, invoice.pk),
            "http://happy-dev.fr/owl/#title": "new",
            "http://happy-dev.fr/owl/#batches": [
                {
                    "@id": "{}/batchs/{}/".format(base_url, pre_existing_batch.pk),
                    "http://happy-dev.fr/owl/#title": "new",
                    "http://happy-dev.fr/owl/#tasks": [
                        {
                            "@id": "{}/tasks/{}/".format(base_url, pre_existing_task.pk),
                            "http://happy-dev.fr/owl/#title": "new"
                        },
                        {
                            "http://happy-dev.fr/owl/#title": "tache 2"
                        }
                    ]
                },
                {
                    "http://happy-dev.fr/owl/#title": "z",
                }
            ]
        }

        response = self.client.put('/invoices/{}/'.format(invoice.pk), data=json.dumps(body),
                                   content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        self.assertEquals(response.data['title'], "new")
        self.assertEquals(response.data['@id'], invoice.urlid)

        invoice = Invoice.objects.get(pk=invoice.pk)
        self.assertIs(invoice.batches.count(), 2)
        batches = invoice.batches.all().order_by('title')
        self.assertEquals(batches[0].title, "new")
        self.assertEquals(batches[0].urlid, pre_existing_batch.urlid)
        self.assertEquals(batches[1].title, "z")

        self.assertIs(batches[0].tasks.count(), 2)
        tasks = batches[0].tasks.all().order_by('title')
        self.assertEquals(tasks[0].title, "new")
        self.assertEquals(tasks[0].pk, pre_existing_task.pk)
        self.assertEquals(tasks[1].title, "tache 2")

    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/333
    '''def test_update_container_nested_view(self):
        circle = Circle.objects.create(name='test')
        pre_existing = CircleMember.objects.create(user=self.user, circle=circle, is_admin=False)
        another_user = get_user_model().objects.create_user(username='u2', email='u2@b.com', password='pw')

        body = {
            "@id": "{}/circles/{}/".format(settings.BASE_URL, circle.pk),
            "http://happy-dev.fr/owl/#name": "Updated Name",
            "http://happy-dev.fr/owl/#members": {
                "ldp:contains": [
                    {"@id": "{}/circle-members/{}/".format(settings.BASE_URL, pre_existing.pk),
                     "http://happy-dev.fr/owl/#is_admin": True},
                    {"http://happy-dev.fr/owl/#user": {"@id": another_user.urlid},
                     "http://happy-dev.fr/owl/#is_admin": False},
                ]
            }
        }

        response = \
            self.client.put('/circles/{}/'.format(circle.pk), data=json.dumps(body), content_type='application/ld+json')
        print(str(self.user.urlid))
        print(str(response.data))
        self.assertEqual(response.status_code, 200)

        self.assertEquals(response.data['name'], circle.name)
        self.assertEqual(response.data['@id'], circle.urlid)
        self.assertIs(CircleMember.objects.count(), 2)
        self.assertIs(circle.members.count(), 2)
        self.assertIs(circle.team.count(), 2)

        members = circle.members.all().order_by('pk')
        self.assertEqual(members[0].user, self.user)
        self.assertEqual(members[0].urlid, pre_existing.urlid)
        self.assertEqual(members[0].pk, pre_existing.pk)
        self.assertEqual(members[0].is_admin, True)
        self.assertEqual(members[1].user, another_user)
        self.assertEqual(members[1].is_admin, False)'''

