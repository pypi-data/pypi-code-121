import json
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase
from djangoldp.tests.models import Circle, CircleMember, Project, DateModel, DateChild
from djangoldp.models import Activity, Follower


class TestsInbox(APITestCase):

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com',
                                                         password='glass onion')

    def _get_activity_request_template(self, type, obj, target=None, origin=None):
        res = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                {"hd": "http://happy-dev.fr/owl/#"}
            ],
            "summary": "Something happened",
            "type": type,
            "actor": {
                "type": "Service",
                "name": "Backlinks Service",
                "inbox": "http://127.0.0.1:8000/inbox/"
            },
            "object": obj
        }

        if target is not None:
            res.update({"target": target})

        if origin is not None:
            res.update({"origin": origin})

        return res

    def _build_target_from_user(self, user):
        return {
            "@type": "foaf:user",
            "name": user.get_full_name(),
            "@id": user.urlid
        }

    def _assert_activity_created(self, response, activity_len=1):
        '''Auxiliary function asserts that the activity was created and returned correctly'''
        activities = Activity.objects.all()
        self.assertEquals(len(activities), activity_len)
        self.assertIn(response["Location"], activities.values_list('urlid', flat=True))

    def _assert_follower_created(self, local_urlid, external_urlid):
        existing_followers = Follower.objects.filter(object=local_urlid).values_list('follower', flat=True)
        self.assertTrue(external_urlid in existing_followers)

    #
    #   CREATE ACTIVITY
    #
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_create_activity_circle(self):
        obj = {
            "@type": "hd:circle",
            "@id": "https://distant.com/circles/1/",
            "owner": {
                "@type": "foaf:user",
                "@id": self.user.urlid
            }
        }
        payload = self._get_activity_request_template("Create", obj)

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

        # assert that the circle was created and the user associated as owner
        circles = Circle.objects.all()
        self.assertEquals(len(circles), 1)
        self.assertIn("https://distant.com/circles/1/", circles.values_list('urlid', flat=True))
        self.assertEqual(circles[0].owner, self.user)
        self._assert_activity_created(response)

        # assert external circle member now following local user
        self.assertEquals(Follower.objects.count(), 1)
        self._assert_follower_created(self.user.urlid, "https://distant.com/circles/1/")

    # tests creation, and tests that consequential creation also happens
    # i.e. that I pass it an external circle which it doesn't know about, and it creates that too
    def test_create_activity_circle_member(self):
        obj = {
            "@type": "hd:circlemember",
            "@id": "https://distant.com/circlemembers/1/",
            "user": {
                "@type": "foaf:user",
                "@id": self.user.urlid
            },
            "circle": {
                "@type": "hd:circle",
                "@id": "https://distant.com/circles/1/"
            }
        }
        payload = self._get_activity_request_template("Create", obj)

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

        # assert that the circle was created and the user associated as member
        circles = Circle.objects.all()
        self.assertEquals(len(circles), 1)
        self.assertIn("https://distant.com/circles/1/", circles.values_list('urlid', flat=True))
        self.assertTrue(circles[0].members.filter(user=self.user).exists())
        self._assert_activity_created(response)

        # assert external circle member now following local user
        self._assert_follower_created(self.user.urlid, "https://distant.com/circlemembers/1/")

    # sender has sent a circle with a local user that doesn't exist
    def test_create_activity_circle_local(self):
        urlid = '{}/{}'.format(settings.SITE_URL, 'someonewhodoesntexist')
        obj = {
            "@type": "hd:circle",
            "@id": "https://distant.com/circles/1/",
            "owner": {
                "@type": "foaf:user",
                "@id": urlid
            }
        }
        payload = self._get_activity_request_template("Create", obj)

        prior_users_length = get_user_model().objects.count()

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

        # assert that the circle was not created neither a backlinked user
        self.assertEquals(Circle.objects.count(), 0)
        self.assertEquals(get_user_model().objects.count(), prior_users_length)

    #
    #   ADD ACTIVITIES
    #
    # project model has a direct many-to-many with User
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_add_activity_project(self):
        obj = {
            "@type": "hd:project",
            "@id": "https://distant.com/projects/1/"
        }
        payload = self._get_activity_request_template("Add", obj, self._build_target_from_user(self.user))

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

        # assert that the project backlink(s) & activity were created
        projects = Project.objects.all()
        user_projects = self.user.projects.all()
        self.assertEquals(len(projects), 1)
        self.assertEquals(len(user_projects), 1)
        self.assertIn("https://distant.com/projects/1/", projects.values_list('urlid', flat=True))
        self.assertIn("https://distant.com/projects/1/", user_projects.values_list('urlid', flat=True))
        self._assert_activity_created(response)

        # assert external circle member now following local user
        self.assertEquals(Follower.objects.count(), 1)
        self._assert_follower_created(self.user.urlid, "https://distant.com/projects/1/")

    # circle model has a many-to-many with user, through an intermediate model
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_add_activity_circle(self):
        ext_circlemember_urlid = "https://distant.com/circle-members/1/"
        ext_circle_urlid = "https://distant.com/circles/1/"

        obj = {
            "@type": "hd:circlemember",
            "@id": ext_circlemember_urlid,
            "user": {
              "@type": "foaf:user",
              "@id": self.user.urlid
            },
            "circle": {
                "@type": "hd:circle",
                "@id": ext_circle_urlid
            }
        }
        payload = self._get_activity_request_template("Add", obj, self._build_target_from_user(self.user))

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload), content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self.assertEqual(response.status_code, 201)

        # assert that the circle backlink(s) & activity were created
        circles = Circle.objects.all()
        user_circles = self.user.circles.all()
        self.assertEquals(len(circles), 1)
        self.assertEquals(len(user_circles), 1)
        self.assertIn(ext_circle_urlid, circles.values_list('urlid', flat=True))
        self.assertIn(ext_circlemember_urlid, user_circles.values_list('urlid', flat=True))
        self._assert_activity_created(response)

        # assert external circle member now following local user
        self.assertEquals(Follower.objects.count(), 1)
        self._assert_follower_created(self.user.urlid, ext_circlemember_urlid)

    # test sending an add activity when the backlink already exists
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_add_activity_object_already_added(self):
        circle = Circle.objects.create(urlid="https://distant.com/circles/1/")
        cm = CircleMember.objects.create(urlid="https://distant.com/circle-members/1/", circle=circle, user=self.user)

        obj = {
            "@type": "hd:circlemember",
            "@id": "https://distant.com/circle-members/1/",
            "user": {
                "@type": "foaf:user",
                "@id": self.user.urlid
            },
            "circle": {
                "@type": "hd:circle",
                "@id": "https://distant.com/circles/1/"
            }
        }
        payload = self._get_activity_request_template("Add", obj, self._build_target_from_user(self.user))
        prior_count = Activity.objects.count()

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self.assertEqual(response.status_code, 201)

        # assert that the circle backlink(s) & activity were created
        circles = Circle.objects.all()
        user_circles = self.user.circles.all()
        self.assertEquals(len(circles), 1)
        self.assertEquals(len(user_circles), 1)
        self.assertIn("https://distant.com/circles/1/", circles.values_list('urlid', flat=True))
        self.assertIn("https://distant.com/circle-members/1/", user_circles.values_list('urlid', flat=True))
        self._assert_activity_created(response)
        self.assertEqual(Activity.objects.count(), prior_count + 1)

        # assert that followers exist for the external urlids
        self.assertEquals(Follower.objects.count(), 1)
        self._assert_follower_created(self.user.urlid, cm.urlid)

    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/250
    def test_add_activity_str_parameter(self):
        payload = self._get_activity_request_template("Add", "https://distant.com/somethingunknown/1/",
                                                      self._build_target_from_user(self.user))
        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self.assertEqual(response.status_code, 400)

    # TODO: may pass an object without an explicit urlid e.g. Person actor, or Collection target

    # error behaviour - unknown model
    def test_add_activity_unknown(self):
        obj = {
            "@type": "hd:somethingunknown",
            "@id": "https://distant.com/somethingunknown/1/"
        }
        payload = self._get_activity_request_template("Add", obj, self._build_target_from_user(self.user))
        response = self.client.post('/inbox/',
                                    data=json.dumps(payload), content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self.assertEqual(response.status_code, 404)

    def _test_fail_behaviour(self, response, status_code=400):
        self.assertEqual(response.status_code, 400)

        # assert that nothing was created
        self.assertEquals(Circle.objects.count(), 0)
        self.assertEquals(self.user.circles.count(), 0)
        self.assertEqual(Activity.objects.count(), 0)
        self.assertEquals(Follower.objects.count(), 0)

    # error behaviour - invalid url
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_add_activity_empty_url(self):
        # an invalid url
        ext_circlemember_urlid = "https://distant.com/circle-members/1/"
        ext_circle_urlid = ""

        obj = {
            "@type": "hd:circlemember",
            "@id": ext_circlemember_urlid,
            "user": {
                "@type": "foaf:user",
                "@id": self.user.urlid
            },
            "circle": {
                "@type": "hd:circle",
                "@id": ext_circle_urlid
            }
        }
        payload = self._get_activity_request_template("Add", obj, self._build_target_from_user(self.user))

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self._test_fail_behaviour(response, 400)

    # error behaviour - invalid url
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_add_activity_invalid_url(self):
        # an invalid url
        ext_circlemember_urlid = "https://distant.com/circle-members/1/"
        ext_circle_urlid = "not$valid$url"

        obj = {
            "@type": "hd:circlemember",
            "@id": ext_circlemember_urlid,
            "user": {
                "@type": "foaf:user",
                "@id": self.user.urlid
            },
            "circle": {
                "@type": "hd:circle",
                "@id": ext_circle_urlid
            }
        }
        payload = self._get_activity_request_template("Add", obj, self._build_target_from_user(self.user))

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self._test_fail_behaviour(response, 400)

    # error behaviour - None url
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_add_activity_none_url(self):
        # an invalid url
        ext_circlemember_urlid = "https://distant.com/circle-members/1/"
        ext_circle_urlid = None

        obj = {
            "@type": "hd:circlemember",
            "@id": ext_circlemember_urlid,
            "user": {
                "@type": "foaf:user",
                "@id": self.user.urlid
            },
            "circle": {
                "@type": "hd:circle",
                "@id": ext_circle_urlid
            }
        }
        payload = self._get_activity_request_template("Add", obj, self._build_target_from_user(self.user))

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self._test_fail_behaviour(response, 400)

    # missing @id on a sub-object
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_add_activity_no_id(self):
        ext_circlemember_urlid = "https://distant.com/circle-members/1/"

        obj = {
            "@type": "hd:circlemember",
            "@id": ext_circlemember_urlid,
            "user": {
                "@type": "foaf:user",
                "@id": self.user.urlid
            },
            "circle": {
                "@type": "hd:circle"
            }
        }
        payload = self._get_activity_request_template("Add", obj, self._build_target_from_user(self.user))

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self._test_fail_behaviour(response, 400)

    # missing @type on a sub-object
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_add_activity_no_type(self):
        ext_circlemember_urlid = "https://distant.com/circle-members/1/"

        obj = {
            "@type": "hd:circlemember",
            "@id": ext_circlemember_urlid,
            "user": {
                "@type": "foaf:user",
                "@id": self.user.urlid
            },
            "circle": {
                "@id": "https://distant.com/circles/1/"
            }
        }
        payload = self._get_activity_request_template("Add", obj, self._build_target_from_user(self.user))

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self._test_fail_behaviour(response, 404)

    def test_invalid_activity_missing_actor(self):
        payload = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                {"hd": "http://happy-dev.fr/owl/#"}
            ],
            "summary": "Test was added to Test Circle",
            "type": "Add",
            "object": {
                "@type": "hd:somethingunknown",
                "@id": "https://distant.com/somethingunknown/1/"
            },
            "target": {
                "@type": "foaf:user",
                "@id": self.user.urlid
            }
        }

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self.assertEqual(response.status_code, 400)

    # test activity setting unsafe fields in object
    def test_unsafe_fields_in_activity(self):
        obj = {
            "@type": "hd:project",
            "@id": "https://distant.com/projects/1/",
            "pk": 100,
            "id": 100
        }
        payload = self._get_activity_request_template("Add", obj, self._build_target_from_user(self.user))
        response = self.client.post('/inbox/',
                                    data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

        # assert that the project backlink(s) & activity were created
        projects = Project.objects.all()
        user_projects = self.user.projects.all()
        self.assertEquals(len(projects), 1)
        self.assertEquals(len(user_projects), 1)
        self.assertIn("https://distant.com/projects/1/", projects.values_list('urlid', flat=True))
        self.assertIn("https://distant.com/projects/1/", user_projects.values_list('urlid', flat=True))
        self._assert_activity_created(response)
        backlink = Project.objects.get(urlid="https://distant.com/projects/1/")
        self.assertNotEqual(backlink.pk, 100)

    def test_missing_not_null_field_activity(self):
        # DateChild must not have a null reference to parent
        # and parent must not have a null field 'date', which here is missing
        obj = {
            "@type": "hd:datechild",
            "@id": "https://distant.com/datechilds/1/",
            "parent": {
                "@type": "hd:date",
                "@id": "https://distant.com/dates/1/"
            }
        }
        payload = self._get_activity_request_template("Create", obj)

        response = self.client.post('/inbox/', data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        dates = DateModel.objects.all()
        date_children = DateChild.objects.all()
        self.assertEqual(len(dates), 0)
        self.assertEqual(len(date_children), 0)

    #
    #   REMOVE & DELETE ACTIVITIES
    #
    # project model has a direct many-to-many with User
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_remove_activity_project_using_origin(self):
        project = Project.objects.create(urlid="https://distant.com/projects/1/")
        self.user.projects.add(project)
        Follower.objects.create(object=self.user.urlid, inbox='https://distant.com/inbox/',
                                follower=project.urlid, is_backlink=True)
        prior_activity_count = Activity.objects.count()

        obj = {
            "@type": "hd:project",
            "@id": "https://distant.com/projects/1/"
        }
        payload = self._get_activity_request_template("Remove", obj, origin=self._build_target_from_user(self.user))
        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self.assertEqual(response.status_code, 201)

        # assert that the circle backlink(s) were removed & activity were created
        projects = Project.objects.all()
        user_projects = self.user.projects.all()
        self.assertEquals(len(projects), 1)
        self.assertEquals(len(user_projects), 0)
        self.assertIn("https://distant.com/projects/1/", projects.values_list('urlid', flat=True))
        self._assert_activity_created(response, prior_activity_count + 1)
        self.assertEqual(Follower.objects.count(), 0)

    # TODO: test_remove_activity_project_using_target (https://git.startinblox.com/djangoldp-packages/djangoldp/issues/231)

    # error behaviour - project does not exist on user
    def test_remove_activity_nonexistent_project(self):
        Project.objects.create(urlid="https://distant.com/projects/1/")

        obj = {
            "@type": "hd:project",
            "@id": "https://distant.com/projects/1/"
        }
        payload = self._get_activity_request_template("Remove", obj, origin=self._build_target_from_user(self.user))
        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self.assertEqual(response.status_code, 201)
        self._assert_activity_created(response)

    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_removing_object_twice(self):
        project = Project.objects.create(urlid="https://distant.com/projects/1/")
        self.user.projects.add(project)
        prior_count = Activity.objects.all().count()

        # remove once via activity
        obj = {
            "@type": "hd:project",
            "@id": "https://distant.com/projects/1/"
        }
        payload = self._get_activity_request_template("Remove", obj, origin=self._build_target_from_user(self.user))
        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self.assertEqual(response.status_code, 201)
        # received and then sent
        self.assertEqual(Activity.objects.all().count(), prior_count + 2)
        prior_count = Activity.objects.all().count()

        # sending remove activity again
        payload = self._get_activity_request_template("Remove", obj, origin=self._build_target_from_user(self.user))
        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        # just received, did not send
        self.assertEqual(Activity.objects.all().count(), prior_count + 1)

    # Delete CircleMember
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX=True)
    def test_delete_activity_circle_using_origin(self):
        circle = Circle.objects.create(urlid="https://distant.com/circles/1/", allow_create_backlink=False)
        cm = CircleMember.objects.create(urlid="https://distant.com/circle-members/1/",circle=circle, user=self.user)
        Follower.objects.create(object=self.user.urlid, inbox='https://distant.com/inbox/',
                                follower=cm.urlid, is_backlink=True)

        obj = {
            "@type": "hd:circlemember",
            "@id": "https://distant.com/circle-members/1/",
            "user": {
                "@type": "foaf:user",
                "@id": self.user.urlid
            },
            "circle": {
                "@type": "hd:circle",
                "@id": "https://distant.com/circles/1/"
            }
        }
        payload = self._get_activity_request_template("Delete", obj)
        response = self.client.post('/inbox/',
                                    data=json.dumps(payload),
                                    content_type='application/ld+json;profile="https://www.w3.org/ns/activitystreams"')
        self.assertEqual(response.status_code, 201)

        # assert that the CircleMember was deleted and activity was created
        circles = Circle.objects.all()
        user_circles = self.user.circles.all()
        self.assertEquals(len(circles), 1)
        self.assertEquals(CircleMember.objects.count(), 0)
        self.assertEquals(len(user_circles), 0)
        self.assertIn("https://distant.com/circles/1/", circles.values_list('urlid', flat=True))
        self._assert_activity_created(response)
        self.assertEqual(Follower.objects.count(), 0)

    # TODO: test_delete_activity_circle_using_target

    #
    #   UPDATE Activities
    #
    def test_update_activity_circle(self):
        circle = Circle.objects.create(urlid="https://distant.com/circles/1/", owner=self.user)
        self.assertEqual(circle.owner, self.user)

        prior_user_count = get_user_model().objects.count()

        obj = {
            "@type": "hd:circle",
            "@id": "https://distant.com/circles/1/",
            "owner": {
                "@type": "foaf:user",
                "@id": "https://distant.com/users/1/"
            }
        }
        payload = self._get_activity_request_template("Update", obj)
        response = self.client.post('/inbox/',
                                    data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

        # assert that the circle was created and the user associated as owner
        circles = Circle.objects.all()
        users = get_user_model().objects.all()
        self.assertEquals(len(circles), 1)
        self.assertEquals(len(users), prior_user_count + 1)
        distant_user = get_user_model().objects.get(urlid="https://distant.com/users/1/")
        self.assertIn("https://distant.com/circles/1/", circles.values_list('urlid', flat=True))
        self.assertEqual(circles[0].owner, distant_user)
        self._assert_activity_created(response)

    #
    #   FOLLOW activities
    #
    def test_follow_activity(self):
        circle = Circle.objects.create(description='Test Description')
        obj = {
            "@type": "hd:circle",
            "@id": circle.urlid
        }
        payload = self._get_activity_request_template("Follow", obj)

        response = self.client.post('/inbox/',
                                    data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

        # assert that Follower was created with correct values
        followers = Follower.objects.all()
        self.assertEquals(len(followers), 1)
        self._assert_activity_created(response)
        follower = followers[0]
        self.assertEqual("http://127.0.0.1:8000/inbox/", follower.inbox)
        self.assertEqual(circle.urlid, follower.object)

    # test Followers are auto-deleted when the object they're following is deleted
    def test_follower_auto_delete(self):
        circle = Circle.objects.create(description='Test Description')
        Follower.objects.create(object=circle.urlid, inbox="http://127.0.0.1:8000/inbox/")
        followers = Follower.objects.all()
        self.assertEquals(len(followers), 1)
        circle.delete()
        followers = Follower.objects.all()
        self.assertEquals(len(followers), 0)

    #
    #   GET Inbox
    #
    def test_get_inbox(self):
        response = self.client.get('/inbox/')
        self.assertEqual(response.status_code, 405)

    # TODO: GET inbox for specific resource - should return a list of activities sent to this inbox
    # TODO: view to access outbox (https://git.startinblox.com/djangoldp-packages/djangoldp/issues/284)
