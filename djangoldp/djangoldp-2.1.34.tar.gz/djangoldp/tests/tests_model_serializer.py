from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory, APIClient

from djangoldp.serializers import LDPSerializer
from djangoldp.tests.models import Invoice, Batch, ModelTask
from djangoldp.tests.models import Skill, JobOffer, Conversation, Message


class LDPModelSerializerTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com',
                                                         password='glass onion')
        self.client.force_authenticate(user=self.user)

    def _get_serializer_class(self, model, depth, fields):
        meta_args = {'model': model, 'depth': depth, 'fields': fields}

        meta_class = type('Meta', (), meta_args)
        return type(LDPSerializer)('TestSerializer', (LDPSerializer,), {'Meta': meta_class})

    def test_update_container_new_resource_replace(self):
        # 2 pre-existing skills, one will be replaced and the other updated
        redundant_skill = Skill.objects.create(title="to drop", obligatoire="obligatoire", slug="slug1")
        pre_existing_skill = Skill.objects.create(title="to keep", obligatoire="obligatoire", slug="slug2")
        job = JobOffer.objects.create(title="job test")
        job.skills.add(redundant_skill)
        job.skills.add(pre_existing_skill)

        post = {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, job.slug),
               "title": "job test updated",
               "skills": {
                   "ldp:contains": [
                       {"title": "new skill", "obligatoire": "okay"},
                       {"@id": "{}/skills/{}/".format(settings.BASE_URL, pre_existing_skill.slug), "title": "z"},
                   ]}
               }

        serializer_class = self._get_serializer_class(JobOffer, 2, ("@id", "title", "skills"))
        serializer = serializer_class(data=post, instance=job)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        self.assertEquals(result.title, "job test updated")
        self.assertIs(result.skills.count(), 2)
        skills = result.skills.all().order_by("title")
        self.assertEquals(skills[0].title, "new skill")
        self.assertEquals(skills[0].obligatoire, "okay")
        self.assertEquals(skills[1].title, "z") # updated
        self.assertEquals(skills[1].obligatoire, pre_existing_skill.obligatoire)

    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/326
    '''
    def test_update_container_edit_and_new_resource_append(self):
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

        serializer_class = self._get_serializer_class(JobOffer, 2, ("@id", "title", "skills"))
        serializer = serializer_class(data=post, instance=job)
        serializer.is_valid(raise_exception=True)
        result = serializer.save(partial=True)

        self.assertEquals(result.title, job.title)
        self.assertIs(result.skills.count(), 3)
        skills = result.skills.all().order_by('title')
        self.assertEquals(skills[0].title, "new skill") # new skill
        self.assertEquals(skills[1].title, pre_existing_skill_a.title) # old skill unchanged
        self.assertEquals(skills[2].title, "z") # updated
        self.assertEquals(skills[2].obligatoire, pre_existing_skill_b.obligatoire) # another field not updated
    '''

    def test_update_container_edit_and_new_external_resources(self):
        job = JobOffer.objects.create(title="job test")
        pre_existing_external = Skill.objects.create(title="to keep", obligatoire="obligatoire",
                                                     urlid="https://external.com/skills/2/")
        job.skills.add(pre_existing_external)

        post = {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, job.slug),
                "skills": {
                    "ldp:contains": [
                        {"@id": "https://external.com/skills/1/", "title": "external skill", "obligatoire": "okay"},
                        {"@id": "https://external.com/skills/2/", "title": "to keep", "obligatoire": "okay"},
                    ]}
                }

        serializer_class = self._get_serializer_class(JobOffer, 2, ("@id", "title", "skills"))
        serializer = serializer_class(data=post, instance=job)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        skills = result.skills.all().order_by('urlid')
        self.assertEquals(result.title, job.title)
        self.assertEqual(result.pk, job.pk)
        self.assertEqual(result.urlid, job.urlid)
        self.assertIs(result.skills.count(), 2)
        self.assertEquals(skills[0].title, "external skill")  # new skill
        self.assertEquals(skills[0].urlid, "https://external.com/skills/1/")  # new skill
        self.assertEquals(skills[0].obligatoire, "okay")
        self.assertEquals(skills[1].title, pre_existing_external.title)  # old skill unchanged
        self.assertEquals(skills[1].urlid, pre_existing_external.urlid)
        self.assertEquals(skills[1].obligatoire, "okay")
        self.assertEquals(skills[1].pk, pre_existing_external.pk)

    def test_update_container_attach_existing_resource(self):
        job = JobOffer.objects.create(title="job test")
        another_job = JobOffer.objects.create(title="job2")
        pre_existing_skill = Skill.objects.create(title="to keep", obligatoire="obligatoire")
        another_job.skills.add(pre_existing_skill)

        self.assertIs(job.skills.count(), 0)

        post = {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, job.slug),
                "skills": {
                    "ldp:contains": [
                        {"@id": "{}/skills/{}/".format(settings.BASE_URL, pre_existing_skill.slug)},
                    ]}
                }

        serializer_class = self._get_serializer_class(JobOffer, 2, ("@id", "title", "skills"))
        serializer = serializer_class(data=post, instance=job)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        skills = result.skills.all().order_by('urlid')
        self.assertEquals(result.title, job.title)
        self.assertEqual(result.pk, job.pk)
        self.assertEqual(result.urlid, job.urlid)
        self.assertIs(result.skills.count(), 1)
        self.assertEquals(skills[0].urlid, pre_existing_skill.urlid)
        self.assertIs(another_job.skills.count(), 1)
        self.assertIs(Skill.objects.count(), 1)

    def test_update_container_attach_existing_resource_external(self):
        job = JobOffer.objects.create(title="job test")
        another_job = JobOffer.objects.create(title="job2")
        pre_existing_external = Skill.objects.create(title="to keep", obligatoire="obligatoire",
                                                     urlid="https://external.com/skills/2/")
        another_job.skills.add(pre_existing_external)

        self.assertIs(job.skills.count(), 0)

        post = {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, job.slug),
                "skills": {
                    "ldp:contains": [
                        {"@id": pre_existing_external.urlid},
                    ]}
                }

        serializer_class = self._get_serializer_class(JobOffer, 2, ("@id", "title", "skills"))
        serializer = serializer_class(data=post, instance=job)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        skills = result.skills.all().order_by('urlid')
        self.assertEquals(result.title, job.title)
        self.assertEqual(result.pk, job.pk)
        self.assertEqual(result.urlid, job.urlid)
        self.assertIs(result.skills.count(), 1)
        self.assertEquals(skills[0].urlid, pre_existing_external.urlid)
        self.assertIs(another_job.skills.count(), 1)
        self.assertIs(Skill.objects.count(), 1)

    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/344
    def test_update_container_mismatched_type_urlid(self):
        job = JobOffer.objects.create(title="job test")
        another_job = JobOffer.objects.create(title="job2")

        # contains internal urlid which refers to a different type of object entirely, and one which refers to container
        post = {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, job.slug),
                "skills": {
                    "ldp:contains": [
                        {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, another_job.slug)},
                    ]}
                }

        serializer_class = self._get_serializer_class(JobOffer, 2, ("@id", "title", "skills"))
        serializer = serializer_class(data=post, instance=job)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/345
    '''
    def test_update_container_mismatched_type_urlid_2(self):
        job = JobOffer.objects.create(title="job test")

        # contains internal urlid which refers to a container
        post = {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, job.slug),
                "skills": {
                    "ldp:contains": [
                        {"@id": "{}/skills/".format(settings.BASE_URL)},
                    ]}
                }

        serializer_class = self._get_serializer_class(JobOffer, 2, ("@id", "title", "skills"))
        serializer = serializer_class(data=post, instance=job)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        # TODO: assert correct error is thrown
    '''

    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/344
    def test_update_container_mismatched_type_urlid_external(self):
        job = JobOffer.objects.create(title="job test")

        # contains external mismatched urlids which refers to a container
        post = {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, job.slug),
                "skills": {
                    "ldp:contains": [
                        {"@id": "https://external.com/skills/"},
                    ]}
                }

        serializer_class = self._get_serializer_class(JobOffer, 2, ("@id", "title", "skills"))
        serializer = serializer_class(data=post, instance=job)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/346
    '''def test_update_container_attach_nonexistent_local_resource(self):
        job = JobOffer.objects.create(title="job test")

        self.assertEqual(JobOffer.objects.count(), 1)
        self.assertEqual(job.skills.count(), 0)
        self.assertEqual(Skill.objects.count(), 0)

        post = {"@id": "{}/job-offers/{}/".format(settings.BASE_URL, job.slug),
                "skills": {
                    "ldp:contains": [
                        {"@id": "{}/skills/404/".format(settings.BASE_URL)},
                    ]}
                }

        serializer_class = self._get_serializer_class(JobOffer, 2, ("@id", "title", "skills"))
        serializer = serializer_class(data=post, instance=job)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        self.assertEqual(JobOffer.objects.count(), 1)
        self.assertEqual(job.skills.count(), 0)
        self.assertEqual(Skill.objects.count(), 0)'''

    # CircleMember is different to Skill because it represents a many-to-many relationship via a through model
    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/333
    '''def test_update_m2m_relationship_with_through_model_add_and_edit(self):
        circle = Circle.objects.create(name='test')
        pre_existing = CircleMember.objects.create(user=self.user, circle=circle, is_admin=False)
        another_user = get_user_model().objects.create_user(username='u2', email='u2@b.com', password='pw')

        post = {
            "@id": "{}/circles/{}/".format(settings.BASE_URL, circle.pk),
            "name": "Updated Name",
            "members": {
                "ldp:contains": [
                    {"@id": "{}/circle-members/{}/".format(settings.BASE_URL, pre_existing.pk), "is_admin": True},
                    {"user": {"@id": another_user.urlid }, "is_admin": False},
                ]
            }
        }

        serializer_class = self._get_serializer_class(Circle, 2, ("@id", "name", "description", "members", "team"))
        serializer = serializer_class(data=post, instance=circle)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        self.assertEquals(result.name, circle.name)
        self.assertEqual(result.pk, circle.pk)
        self.assertEqual(result.urlid, circle.urlid)
        self.assertIs(result.members.count(), 2)
        self.assertIs(result.team.count(), 2)

        members = result.members.all().order_by('pk')
        self.assertEqual(members[0].user, self.user)
        self.assertEqual(members[0].urlid, pre_existing.urlid)
        self.assertEqual(members[0].pk, pre_existing.pk)
        self.assertEqual(members[0].is_admin, True)
        self.assertEqual(members[1].user, another_user)
        self.assertEqual(members[1].is_admin, False)

    # TODO: variation on the above using external resources
    def test_update_m2m_relationship_with_through_model_add_and_edit_external_resources(self):
        pass

    # NOTE: this test if failing due to missing the 'invoice_id' field (see #333)
    #  variation of this test exists in tests_update.py with different behaviour
    def test_update_container_twice_nested(self):
        invoice = Invoice.objects.create(title='test')
        pre_existing_batch = Batch.objects.create(title='batch1', invoice=invoice)
        pre_existing_task = ModelTask.objects.create(title='task1', batch=pre_existing_batch)

        post = {
          "@id": "{}/invoices/{}/".format(settings.BASE_URL, invoice.pk),
          "title": "new",
          "batches": [
            {
              "@id": "{}/batchs/{}/".format(settings.BASE_URL, pre_existing_batch.pk),
              "title": "new",
              "tasks": [
                {
                  "@id": "{}/modeltasks/{}/".format(settings.BASE_URL, pre_existing_task.pk),
                  "title": "new"
                },
                {
                  "title": "tache 2"
                }
              ]
            },
            {
              "title": "z",
            }
          ]
        }

        serializer_class = self._get_serializer_class(Invoice, 2, ("@id", "title", "batches"))
        serializer = serializer_class(data=post, instance=invoice)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        self.assertEquals(result.title, "new")
        self.assertEquals(result.urlid, invoice.urlid)
        self.assertEquals(result.pk, invoice.pk)

        self.assertIs(result.batches.count(), 2)
        batches = result.batches.all().order_by('title')
        self.assertEquals(batches[0].title, "new")
        self.assertEquals(batches[0].urlid, pre_existing_batch.urlid)
        self.assertEquals(batches[1].title, "z")

        self.assertIs(batches[0].tasks.count(), 2)
        tasks = batches[0].tasks.all().order_by('title')
        self.assertEquals(tasks[0].title, "new")
        self.assertEquals(tasks[0].urlid, pre_existing_task.urlid)
        self.assertEquals(tasks[1].title, "tache 2")

    # variation on the above test with external resources
    def test_update_container_twice_nested_external_resources(self):
        invoice = Invoice.objects.create(urlid='https://external.com/invoices/1/', title='test')
        pre_existing_batch = Batch.objects.create(urlid='https://external.com/batchs/1/', title='batch1', invoice=invoice)
        pre_existing_task = ModelTask.objects.create(urlid='https://external.com/tasks/1/', title='task1', batch=pre_existing_batch)

        post = {
            "@id": invoice.urlid,
            "title": "new",
            "batches": [
                {
                    "@id": pre_existing_batch.urlid,
                    "title": "new",
                    "tasks": [
                        {
                            "@id": pre_existing_task.urlid,
                            "title": "new"
                        },
                        {
                            "@id": "https://anotherexternal.com/tasks/1/",
                            "title": "tache 2"
                        }
                    ]
                },
                {
                    "@id": "https://yetanotherexternal.com/batchs/1/",
                    "title": "z"
                }
            ]
        }

        serializer_class = self._get_serializer_class(Invoice, 2, ("@id", "title", "batches"))
        serializer = serializer_class(data=post, instance=invoice)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        self.assertEquals(result.title, "new")
        self.assertEquals(result.urlid, invoice.urlid)
        self.assertEquals(result.pk, invoice.pk)

        self.assertIs(result.batches.count(), 2)
        batches = result.batches.all().order_by('title')
        self.assertEquals(batches[0].title, "new")
        self.assertEquals(batches[0].urlid, pre_existing_batch.urlid)
        self.assertEquals(batches[1].title, "z")

        self.assertIs(batches[0].tasks.count(), 2)
        tasks = batches[0].tasks.all().order_by('title')
        self.assertEquals(tasks[0].title, "new")
        self.assertEquals(tasks[0].urlid, pre_existing_task.urlid)
        self.assertEquals(tasks[1].title, "tache 2")'''

    # variation on the test where a field is omitted on each level (no changes are made)
    def test_update_container_twice_nested_no_changes_missing_fields(self):
        invoice = Invoice.objects.create(title='test')
        pre_existing_batch = Batch.objects.create(title='batch1', invoice=invoice)
        pre_existing_task = ModelTask.objects.create(title='task1', batch=pre_existing_batch)

        post = {
            "@id": "{}/invoices/{}/".format(settings.BASE_URL, invoice.pk),
            "batches": [
                {
                    "@id": "{}/batchs/{}/".format(settings.BASE_URL, pre_existing_batch.pk),
                    "tasks": [
                        {
                            "@id": "{}/tasks/{}/".format(settings.BASE_URL, pre_existing_task.pk),
                        }
                    ]
                }
            ]
        }

        serializer_class = self._get_serializer_class(Invoice, 2, ("@id", "title", "batches"))
        serializer = serializer_class(data=post, instance=invoice)
        serializer.is_valid(raise_exception=True)
        result = serializer.save(partial=True)

        self.assertEquals(result.title, invoice.title)
        self.assertEquals(result.urlid, invoice.urlid)
        self.assertEquals(result.pk, invoice.pk)

        self.assertIs(result.batches.count(), 1)
        batches = result.batches.all()
        self.assertEquals(batches[0].title, pre_existing_batch.title)
        self.assertEquals(batches[0].urlid, pre_existing_batch.urlid)

        self.assertIs(batches[0].tasks.count(), 1)
        tasks = batches[0].tasks.all()
        self.assertEquals(tasks[0].title, pre_existing_task.title)

    def test_update_graph_edit_and_new_resource(self):
        redundant_skill = Skill.objects.create(title="to drop", obligatoire="obligatoire", slug="slug1")
        skill1 = Skill.objects.create(title="skill1", obligatoire="obligatoire", slug="slug2")
        skill2 = Skill.objects.create(title="skill2", obligatoire="obligatoire", slug="slug3")
        job1 = JobOffer.objects.create(title="job test", slug="slug4")
        job1.skills.add(redundant_skill)

        job = {"@graph":
            [
                {
                    "@id": "{}/job-offers/{}/".format(settings.BASE_URL, job1.slug),
                    "title": "job test updated",
                    "skills": {
                        "ldp:contains": [
                            {"@id": "{}/skills/{}/".format(settings.BASE_URL, skill1.slug)},
                            {"@id": "{}/skills/{}/".format(settings.BASE_URL, skill2.slug)},
                            {"@id": "_.123"},
                        ]}
                },
                {
                    "@id": "_.123",
                    "title": "new skill",
                    "obligatoire": "okay"
                },
                {
                    "@id": "{}/skills/{}/".format(settings.BASE_URL, skill1.slug),
                },
                {
                    "@id": "{}/skills/{}/".format(settings.BASE_URL, skill2.slug),
                    "title": "skill2 UP"
                }
            ]
        }

        serializer_class = self._get_serializer_class(JobOffer, 2, ("@id", "title", "skills"))
        serializer = serializer_class(data=job, instance=job1)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        skills = result.skills.all().order_by('title')

        self.assertEquals(result.title, "job test updated")
        self.assertIs(result.skills.count(), 3)
        self.assertEquals(skills[0].title, "new skill")  # new skill
        self.assertEquals(skills[1].title, "skill1")  # no change
        self.assertEquals(skills[2].title, "skill2 UP")  # title updated

    def test_update_graph_2(self):
        skill = Skill.objects.create(title="to drop", obligatoire="obligatoire", slug="slug")
        skill1 = Skill.objects.create(title="skill1", obligatoire="obligatoire", slug="slug1")
        skill2 = Skill.objects.create(title="skill2", obligatoire="obligatoire", slug="slug2")
        job1 = JobOffer.objects.create(title="job test", slug="slug1")
        job1.skills.add(skill)

        job = {"@graph":
            [
                {
                    "@id": "{}/job-offers/{}/".format(settings.BASE_URL, job1.slug),
                    "title": "job test updated",
                    "skills": {
                        "@id": "{}/job-offers/{}/skills/".format(settings.BASE_URL, job1.slug)
                    }
                },
                {
                    "@id": "_.123",
                    "title": "new skill",
                    "obligatoire": "okay"
                },
                {
                    "@id": "{}/skills/{}/".format(settings.BASE_URL, skill1.slug),
                },
                {
                    "@id": "{}/skills/{}/".format(settings.BASE_URL, skill2.slug),
                    "title": "skill2 UP"
                },
                {
                    '@id': "{}/job-offers/{}/skills/".format(settings.BASE_URL, job1.slug),
                    "ldp:contains": [
                        {"@id": "{}/skills/{}/".format(settings.BASE_URL, skill1.slug)},
                        {"@id": "{}/skills/{}/".format(settings.BASE_URL, skill2.slug)},
                        {"@id": "_.123"},
                    ]
                }
            ]
        }

        meta_args = {'model': JobOffer, 'depth': 2, 'fields': ("@id", "title", "skills", "slug")}

        meta_class = type('Meta', (), meta_args)
        serializer_class = type(LDPSerializer)('JobOfferSerializer', (LDPSerializer,), {'Meta': meta_class})
        serializer = serializer_class(data=job, instance=job1)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        skills = result.skills.all().order_by('title')

        self.assertEquals(result.title, "job test updated")
        self.assertIs(result.skills.count(), 3)
        self.assertEquals(skills[0].title, "new skill")  # new skill
        self.assertEquals(skills[1].title, "skill1")  # no change
        self.assertEquals(skills[2].title, "skill2 UP")  # title updated
        self.assertEquals(skill, skill._meta.model.objects.get(pk=skill.pk))  # title updated

    def test_update_list_with_reverse_relation(self):
        user1 = get_user_model().objects.create()
        conversation = Conversation.objects.create(description="Conversation 1", author_user=user1)
        message1 = Message.objects.create(text="Message 1", conversation=conversation, author_user=user1)
        message2 = Message.objects.create(text="Message 2", conversation=conversation, author_user=user1)

        json = {"@graph": [
            {
                "@id": "{}/messages/{}/".format(settings.BASE_URL, message1.pk),
                "text": "Message 1 UP"
            },
            {
                "@id": "{}/messages/{}/".format(settings.BASE_URL, message2.pk),
                "text": "Message 2 UP"
            },
            {
                '@id': "{}/conversations/{}/".format(settings.BASE_URL, conversation.pk),
                'description': "Conversation 1 UP",
                "message_set": [
                    {"@id": "{}/messages/{}/".format(settings.BASE_URL, message1.pk)},
                    {"@id": "{}/messages/{}/".format(settings.BASE_URL, message2.pk)},
                ]
            }
        ]
        }

        meta_args = {'model': Conversation, 'depth': 2, 'fields': ("@id", "description", "message_set")}

        meta_class = type('Meta', (), meta_args)
        serializer_class = type(LDPSerializer)('ConversationSerializer', (LDPSerializer,), {'Meta': meta_class})
        serializer = serializer_class(data=json, instance=conversation)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        messages = result.message_set.all().order_by('text')

        self.assertEquals(result.description, "Conversation 1 UP")
        self.assertIs(result.message_set.count(), 2)
        self.assertEquals(messages[0].text, "Message 1 UP")
        self.assertEquals(messages[1].text, "Message 2 UP")

    def test_add_new_element_with_foreign_key_id(self):
        user1 = get_user_model().objects.create()
        conversation = Conversation.objects.create(description="Conversation 1", author_user=user1)
        message1 = Message.objects.create(text="Message 1", conversation=conversation, author_user=user1)
        message2 = Message.objects.create(text="Message 2", conversation=conversation, author_user=user1)

        json = {"@graph": [
            {
                "@id": "{}/messages/{}/".format(settings.BASE_URL, message1.pk),
                "text": "Message 1 UP",
                "author_user": {
                    '@id': "{}/users/{}/".format(settings.BASE_URL, user1.pk)
                }
            },
            {
                "@id": "{}/messages/{}/".format(settings.BASE_URL, message2.pk),
                "text": "Message 2 UP",
                "author_user": {
                    '@id': user1.urlid
                }
            },
            {
                "@id": "_:b1",
                "text": "Message 3 NEW",
                "author_user": {
                    '@id': user1.urlid
                }
            },
            {
                '@id': "{}/conversations/{}/".format(settings.BASE_URL, conversation.pk),
                "author_user": {
                    '@id': user1.urlid
                },
                'description': "Conversation 1 UP",
                'message_set': {
                    "@id": "{}/conversations/{}/message_set/".format(settings.BASE_URL, conversation.pk)
                }
            },
            {
                '@id': "{}/conversations/{}/message_set/".format(settings.BASE_URL, conversation.pk),
                "ldp:contains": [
                    {"@id": "{}/messages/{}/".format(settings.BASE_URL, message1.pk)},
                    {"@id": "{}/messages/{}/".format(settings.BASE_URL, message2.pk)},
                    {"@id": "_:b1"}
                ]
            }
        ]
        }

        meta_args = {'model': Conversation, 'depth': 2, 'fields': ("@id", "description", "message_set")}

        meta_class = type('Meta', (), meta_args)
        serializer_class = type(LDPSerializer)('ConversationSerializer', (LDPSerializer,), {'Meta': meta_class})
        serializer = serializer_class(data=json, instance=conversation)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        messages = result.message_set.all().order_by('text')

        self.assertEquals(result.description, "Conversation 1 UP")
        self.assertIs(result.message_set.count(), 3)
        self.assertEquals(messages[0].text, "Message 1 UP")
        self.assertEquals(messages[1].text, "Message 2 UP")
        self.assertEquals(messages[2].text, "Message 3 NEW")

    # TODO: variation on https://git.startinblox.com/djangoldp-packages/djangoldp/issues/344
    '''def test_update_container_invalid_fk_reference_given(self):
        pass'''

    def test_save_m2m_graph_with_many_nested(self):
        invoice = {
            "@graph": [
                {
                    "@id": "./",
                    "batches": {"@id": "_:b381"},
                    "title": "Nouvelle facture",
                    "date": ""
                },
                {
                    "@id": "_:b381",
                    "tasks": {"@id": "_:b382"},
                    "title": "Batch 1"
                },
                {
                    "@id": "_:b382",
                    "title": "Tache 1"
                }
            ]
        }

        meta_args = {'model': Invoice, 'depth': 2, 'fields': ("@id", "title", "batches", "date")}

        meta_class = type('Meta', (), meta_args)
        serializer_class = type(LDPSerializer)('InvoiceSerializer', (LDPSerializer,), {'Meta': meta_class})
        serializer = serializer_class(data=invoice)
        serializer.is_valid()
        result = serializer.save()

        self.assertEquals(result.title, "Nouvelle facture")
        self.assertIs(result.batches.count(), 1)
        self.assertEquals(result.batches.all()[0].title, "Batch 1")
        self.assertIs(result.batches.all()[0].tasks.count(), 1)
        self.assertEquals(result.batches.all()[0].tasks.all()[0].title, "Tache 1")

    def test_save_m2m(self):
        skill1 = Skill.objects.create(title="skill1", obligatoire="obligatoire", slug="slug1")
        skill2 = Skill.objects.create(title="skill2", obligatoire="obligatoire", slug="slug2")

        job = {"title": "job test",
               "slug": "slug1",
               "skills": {
                   "ldp:contains": [
                       {"@id": "{}/skills/{}/".format(settings.BASE_URL, skill1.slug)},
                       {"@id": "{}/skills/{}/".format(settings.BASE_URL, skill2.slug), "title": "skill2 UP"},
                       {"title": "skill3", "obligatoire": "obligatoire", "slug": "slug3"},
                   ]}
               }

        meta_args = {'model': JobOffer, 'depth': 2, 'fields': ("@id", "title", "skills", "slug")}

        meta_class = type('Meta', (), meta_args)
        serializer_class = type(LDPSerializer)('JobOfferSerializer', (LDPSerializer,), {'Meta': meta_class})
        serializer = serializer_class(data=job)
        serializer.is_valid()
        result = serializer.save()

        self.assertEquals(result.title, "job test")
        self.assertIs(result.skills.count(), 3)
        self.assertEquals(result.skills.all()[0].title, "skill1")  # no change
        self.assertEquals(result.skills.all()[1].title, "skill2 UP")  # title updated
        self.assertEquals(result.skills.all()[2].title, "skill3")  # creation on the fly

    # variation switching the http prefix of the BASE_URL in the request
    @override_settings(BASE_URL='http://happy-dev.fr/')
    def test_save_m2m_switch_base_url_prefix(self):
        skill1 = Skill.objects.create(title="skill1", obligatoire="obligatoire", slug="slug1")

        job = {"title": "job test",
               "slug": "slug1",
               "skills": {
                   "ldp:contains": [
                       {"@id": "https://happy-dev.fr/skills/{}/".format(skill1.slug)},
                   ]}
               }

        meta_args = {'model': JobOffer, 'depth': 2, 'fields': ("@id", "title", "skills", "slug")}

        meta_class = type('Meta', (), meta_args)
        serializer_class = type(LDPSerializer)('JobOfferSerializer', (LDPSerializer,), {'Meta': meta_class})
        serializer = serializer_class(data=job)
        serializer.is_valid()
        result = serializer.save()

        self.assertEquals(result.title, "job test")
        self.assertIs(result.skills.count(), 1)
        self.assertEquals(result.skills.all()[0].title, "skill1")  # no change

    def test_save_m2m_graph_simple(self):
        job = {"@graph": [
            {"title": "job test", "slug": "slugjob",
             },
        ]}

        meta_args = {'model': JobOffer, 'depth': 2, 'fields': ("@id", "title", "skills", "slug")}

        meta_class = type('Meta', (), meta_args)
        serializer_class = type(LDPSerializer)('JobOfferSerializer', (LDPSerializer,), {'Meta': meta_class})
        serializer = serializer_class(data=job)
        serializer.is_valid()
        result = serializer.save()

        self.assertEquals(result.title, "job test")
        self.assertIs(result.skills.count(), 0)

    def test_save_m2m_graph_with_nested(self):
        skill1 = Skill.objects.create(title="skill1", obligatoire="obligatoire", slug="a")
        skill2 = Skill.objects.create(title="skill2", obligatoire="obligatoire", slug="b")

        job = {"@graph": [
            {"title": "job test",
             "slug": "slugj",
             "skills": {"@id": "_.123"}
             },
            {"@id": "_.123", "title": "skill3 NEW", "obligatoire": "obligatoire", "slug": "skill3"},
        ]}

        meta_args = {'model': JobOffer, 'depth': 2, 'fields': ("@id", "title", "skills", "slug")}

        meta_class = type('Meta', (), meta_args)
        serializer_class = type(LDPSerializer)('JobOfferSerializer', (LDPSerializer,), {'Meta': meta_class})
        serializer = serializer_class(data=job)
        serializer.is_valid()
        result = serializer.save()

        self.assertEquals(result.title, "job test")
        self.assertIs(result.skills.count(), 1)
        self.assertEquals(result.skills.all()[0].title, "skill3 NEW")  # creation on the fly

    def test_save_without_nested_fields(self):
        skill1 = Skill.objects.create(title="skill1", obligatoire="obligatoire", slug="a")
        skill2 = Skill.objects.create(title="skill2", obligatoire="obligatoire", slug="b")
        job = {"title": "job test", "slug": "c"}

        meta_args = {'model': JobOffer, 'depth': 2, 'fields': ("@id", "title", "skills", "slug")}

        meta_class = type('Meta', (), meta_args)
        serializer_class = type(LDPSerializer)('JobOfferSerializer', (LDPSerializer,), {'Meta': meta_class})
        serializer = serializer_class(data=job)
        serializer.is_valid()
        result = serializer.save()

        self.assertEquals(result.title, "job test")
        self.assertIs(result.skills.count(), 0)

    def test_save_on_sub_iri(self):
        """
            POST /job-offers/1/skills/
        """
        job = JobOffer.objects.create(title="job test")
        skill = {"title": "new SKILL"}

        meta_args = {'model': Skill, 'depth': 2, 'fields': ("@id", "title")}

        meta_class = type('Meta', (), meta_args)
        serializer_class = type(LDPSerializer)('SkillSerializer', (LDPSerializer,), {'Meta': meta_class})
        serializer = serializer_class(data=skill)
        serializer.is_valid()
        kwargs = {}
        kwargs['joboffer'] = job
        result = serializer.save(**kwargs)

        self.assertEquals(result.title, "new SKILL")
        self.assertIs(result.joboffer_set.count(), 1)
        self.assertEquals(result.joboffer_set.get(), job)
        self.assertIs(result.joboffer_set.get().skills.count(), 1)
