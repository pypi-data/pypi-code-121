import uuid
import time
import copy
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase
from djangoldp.tests.models import Circle, Project
from djangoldp.models import Activity, ScheduledActivity
from djangoldp.activities.services import BACKLINKS_ACTOR, ActivityPubService, ActivityQueueService


class TestsBacklinksService(APITestCase):

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.local_user = get_user_model().objects.create_user(username='john', email='jlennon@beatles.com',
                                                               password='glass onion')

    def _get_random_external_user(self):
        '''Auxiliary function creates a user with random external urlid and returns it'''
        username = str(uuid.uuid4())
        email = username + '@test.com'
        urlid = 'https://distant.com/users/' + username
        return get_user_model().objects.create_user(username=username, email=email, password='test', urlid=urlid)

    # TODO: inbox discovery (https://git.startinblox.com/djangoldp-packages/djangoldp/issues/233)

    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_local_object_with_distant_foreign_key(self):
        # a local Circle with a distant owner
        local_circle = Circle.objects.create(description='Test')
        external_user = self._get_random_external_user()
        local_circle.owner = external_user
        local_circle.save()

        # assert that a activity was sent
        self.assertEqual(Activity.objects.all().count(), 1)

        # reset to a local user, another (update) activity should be sent
        local_circle.owner = self.local_user
        local_circle.save()
        self.assertEqual(Activity.objects.all().count(), 2)

        # external user should no longer be following the object. A further update should not send an activity
        # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/257
        '''another_user = get_user_model().objects.create_user(username='test', email='test@test.com',
                                                            password='glass onion')
        local_circle.owner = another_user
        local_circle.save()
        self.assertEqual(Activity.objects.all().count(), 2)'''

        # re-add the external user as owner
        local_circle.owner = external_user
        local_circle.save()

        # delete parent
        local_circle.delete()
        self.assertEqual(Activity.objects.all().count(), 4)

    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_local_object_with_external_m2m_join_leave(self):
        # a local project with three distant users
        project = Project.objects.create(description='Test')
        external_a = self._get_random_external_user()
        external_b = self._get_random_external_user()
        external_c = self._get_random_external_user()
        project.members.add(external_a)
        project.members.add(external_b)
        project.members.add(external_c)
        self.assertEqual(Activity.objects.all().count(), 3)

        # remove one individual
        project.members.remove(external_a)
        self.assertEqual(Activity.objects.all().count(), 4)

        # clear the rest
        project.members.clear()
        self.assertEqual(Activity.objects.all().count(), 6)
        prior_count = Activity.objects.all().count()

        # once removed I should not be following the object anymore
        project.delete()
        self.assertEqual(Activity.objects.all().count(), prior_count)

    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_local_object_with_external_m2m_delete_parent(self):
        project = Project.objects.create(description='Test')
        external_a = self._get_random_external_user()
        project.members.add(external_a)
        prior_count = Activity.objects.all().count()

        project.delete()
        self.assertEqual(Activity.objects.all().count(), prior_count + 1)

    # test that older ScheduledActivity is discarded for newer ScheduledActivity
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_old_invalid_scheduled_activity_discarded(self):

        def send_two_activities_and_assert_old_discarded(obj):
            # there are two scheduled activities with the same object, (and different time stamps)
            old_activity = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Create', summary='old')
            old_scheduled = ActivityQueueService._save_sent_activity(old_activity, ScheduledActivity)

            new_activity = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Update', summary='new')
            new_scheduled = ActivityQueueService._save_sent_activity(new_activity, ScheduledActivity)

            # both are sent to the ActivityQueueService
            ActivityQueueService._activity_queue_worker('http://127.0.0.1:8001/idontexist/', old_scheduled)
            time.sleep(0.1)
            ActivityQueueService._activity_queue_worker('http://127.0.0.1:8001/idontexist/', new_scheduled)

            time.sleep(0.1)
            # assert that all scheduled activities were cleaned up
            self.assertEquals(ScheduledActivity.objects.count(), 0)

            # assert that ONLY the newly scheduled activity was sent
            activities = Activity.objects.all()
            self.assertEquals(Activity.objects.count(), 1)
            astream = activities[0].to_activitystream()
            self.assertEquals(astream['summary'], new_activity['summary'])
            activities[0].delete()

        # variation using expanded syntax
        obj = {
            '@id': 'https://test.com/users/test/'
        }
        send_two_activities_and_assert_old_discarded(obj)

        # variation using id-only syntax
        obj = 'https://test.com/users/test/'
        send_two_activities_and_assert_old_discarded(obj)

    # test that older ScheduledActivity is still sent if it's on a different object
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_old_valid_scheduled_activity_sent(self):
        # there are two scheduled activities with different objects
        obj = 'https://test.com/users/test1/'
        activity_a = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Create', summary='A')
        scheduled_a = ActivityQueueService._save_sent_activity(activity_a, ScheduledActivity)

        obj = 'https://test.com/users/test2/'
        activity_b = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Create', summary='B')
        scheduled_b = ActivityQueueService._save_sent_activity(activity_b, ScheduledActivity)

        # both are sent to the same inbox
        ActivityQueueService._activity_queue_worker('http://127.0.0.1:8001/idontexist/', scheduled_a)
        ActivityQueueService._activity_queue_worker('http://127.0.0.1:8001/idontexist/', scheduled_b)

        # assert that both scheduled activities were sent, and the scheduled activities were cleaned up
        self.assertEquals(ScheduledActivity.objects.count(), 0)
        self.assertEquals(Activity.objects.count(), 2)

    # variation on the previous test where the two activities are working on different models (using the same object)
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_old_valid_scheduled_activity_sent_same_object(self):
        obj = 'https://test.com/users/test1/'
        target = {'@type': 'hd:skill', '@id': 'https://api.test1.startinblox.com/skills/4/'}
        activity_a = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Add', summary='A', target=target)
        scheduled_a = ActivityQueueService._save_sent_activity(activity_a, ScheduledActivity)

        obj = 'https://test.com/users/test1/'
        target = {'@type': 'hd:joboffer', '@id': 'https://api.test1.startinblox.com/job-offers/1/'}
        activity_b = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Add', summary='B', target=target)
        scheduled_b = ActivityQueueService._save_sent_activity(activity_b, ScheduledActivity)

        # both are sent to the same inbox
        ActivityQueueService._activity_queue_worker('http://127.0.0.1:8001/idontexist/', scheduled_a)
        ActivityQueueService._activity_queue_worker('http://127.0.0.1:8001/idontexist/', scheduled_b)

        # assert that both scheduled activities were sent, and the scheduled activities were cleaned up
        self.assertEquals(ScheduledActivity.objects.count(), 0)
        self.assertEquals(Activity.objects.count(), 2)

    # variation using an Add and a Remove (one defines target, the other origin)
    # also tests that an unnecessary add is not sent
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_matching_origin_and_target_not_sent(self):
        a = {'type': 'Add', 'actor': {'type': 'Service', 'name': 'Backlinks Service'},
             'object': {'@type': 'foaf:user', '@id': 'https://api.test2.startinblox.com/users/calum/'},
             'target': {'@type': 'hd:skill', '@id': 'https://api.test1.startinblox.com/skills/3/'}}
        scheduled_a = ActivityQueueService._save_sent_activity(a, ScheduledActivity)
        b = {'type': 'Remove', 'actor': {'type': 'Service', 'name': 'Backlinks Service'},
             'object': {'@type': 'foaf:user', '@id': 'https://api.test2.startinblox.com/users/calum/'},
             'origin': {'@type': 'hd:skill', '@id': 'https://api.test1.startinblox.com/skills/3/'}}
        scheduled_b = ActivityQueueService._save_sent_activity(b, ScheduledActivity)

        # both are sent to the same inbox
        ActivityQueueService._activity_queue_worker('http://127.0.0.1:8001/idontexist/', scheduled_a)
        ActivityQueueService._activity_queue_worker('http://127.0.0.1:8001/idontexist/', scheduled_b)

        # assert that both scheduled activities were sent, and the scheduled activities were cleaned up
        self.assertEquals(ScheduledActivity.objects.count(), 0)
        self.assertEquals(Activity.objects.count(), 1)

    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_unnecessary_add_not_sent(self):
        # an add activity was sent previously
        a = {'type': 'Add', 'actor': {'type': 'Service', 'name': 'Backlinks Service'},
             'object': {'@type': 'foaf:user', '@id': 'https://api.test2.startinblox.com/users/calum/'},
             'target': {'@type': 'hd:skill', '@id': 'https://api.test1.startinblox.com/skills/3/'}}
        ActivityQueueService._save_activity_from_response({'status_code': '201'}, 'https://distant.com/inbox/', a)

        # no remove has since been sent, but a new Add is scheduled
        scheduled_b = ActivityQueueService._save_sent_activity(a, ScheduledActivity, success=False, type='add',
                                                               external_id='https://distant.com/inbox/')
        ActivityQueueService._activity_queue_worker('https://distant.com/inbox/', scheduled_b)

        # assert that only the previous activity was sent, and the scheduled activites cleaned up
        self.assertEquals(ScheduledActivity.objects.count(), 0)
        self.assertEquals(Activity.objects.count(), 1)

    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_unnecessary_remove_not_sent(self):
        # an remove activity was sent previously
        a = {'type': 'Remove', 'actor': {'type': 'Service', 'name': 'Backlinks Service'},
             'object': {'@type': 'foaf:user', '@id': 'https://api.test2.startinblox.com/users/calum/'},
             'target': {'@type': 'hd:skill', '@id': 'https://api.test1.startinblox.com/skills/3/'}}
        ActivityQueueService._save_activity_from_response({'status_code': '201'}, 'https://distant.com/inbox/', a)

        # no add has since been sent, but a new Remove is scheduled
        scheduled_b = ActivityQueueService._save_sent_activity(a, ScheduledActivity, success=False, type='remove',
                                                               external_id='https://distant.com/inbox/')
        ActivityQueueService._activity_queue_worker('https://distant.com/inbox/', scheduled_b)

        # assert that only the previous activity was sent, and the scheduled activites cleaned up
        self.assertEquals(ScheduledActivity.objects.count(), 0)
        self.assertEquals(Activity.objects.count(), 1)

    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_necessary_add_sent(self):
        # a remove activity was sent previously
        a = {'type': 'Remove', 'actor': {'type': 'Service', 'name': 'Backlinks Service'},
             'object': {'@type': 'foaf:user', '@id': 'https://api.test2.startinblox.com/users/calum/'},
             'target': {'@type': 'hd:skill', '@id': 'https://api.test1.startinblox.com/skills/3/'}}
        ActivityQueueService._save_activity_from_response({'status_code': '201'}, 'https://distant.com/inbox/', a)

        # an add is now being sent
        scheduled_b = ActivityQueueService._save_sent_activity(a, ScheduledActivity, type='add',
                                                               external_id='https://distant.com/inbox/')
        ActivityQueueService._activity_queue_worker('https://distant.com/inbox/', scheduled_b)

        # assert that both activities sent, and the scheduled activites cleaned up
        self.assertEquals(ScheduledActivity.objects.count(), 0)
        self.assertEquals(Activity.objects.count(), 2)

    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_first_add_sent(self):
        # no activity has been sent with this target, before this add
        a = {'type': 'Add', 'actor': {'type': 'Service', 'name': 'Backlinks Service'},
             'object': {'@type': 'foaf:user', '@id': 'https://api.test2.startinblox.com/users/calum/'},
             'target': {'@type': 'hd:skill', '@id': 'https://api.test1.startinblox.com/skills/3/'}}
        scheduled = ActivityQueueService._save_sent_activity(a, ScheduledActivity, success=True, type='add',
                                                             external_id='https://distant.com/inbox/')
        ActivityQueueService._activity_queue_worker('https://distant.com/inbox/', scheduled)

        # assert that the activity was sent, and the scheduled activites cleaned up
        self.assertEquals(ScheduledActivity.objects.count(), 0)
        self.assertEquals(Activity.objects.count(), 1)

    # validate Update activity objects have new info before sending the notification
    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_unnecessary_update_not_sent(self):
        # an object was sent in one activity
        obj = {
            '@type': 'hd:circle',
            '@id': 'https://test.com/circles/8/',
            'owner': {'@id': 'https://distant.com/users/john/',
                      '@type': 'foaf:user'}
        }
        activity_a = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Create', summary='A')
        ActivityQueueService._save_activity_from_response({'status_code': '201'}, 'https://distant.com/inbox/', activity_a)

        # now I'm sending an update, which doesn't change anything about the object
        activity_b = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Create', summary='B')
        scheduled_b = ActivityQueueService._save_sent_activity(activity_b, ScheduledActivity, type='update',
                                                               external_id='https://distant.com/inbox/')

        ActivityQueueService._activity_queue_worker('https://distant.com/inbox/', scheduled_b)

        # assert that only the previous activity was sent, and the scheduled activites cleaned up
        self.assertEquals(ScheduledActivity.objects.count(), 0)
        self.assertEquals(Activity.objects.count(), 1)

    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_necessary_update_is_sent(self):
        # an object was sent in one activity
        obj = {
            '@type': 'hd:circle',
            '@id': 'https://test.com/circles/8/',
            'owner': {'@id': 'https://distant.com/users/john/',
                      '@type': 'foaf:user'}
        }
        activity_a = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Create', summary='A')
        ActivityQueueService._save_activity_from_response({'status_code': '201'}, 'https://distant.com/inbox/', activity_a)

        # now I'm sending an update, which changes the owner of the circle
        obj['owner']['@id'] = 'https://distant.com/users/mark/'
        activity_b = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Create', summary='B')
        scheduled_b = ActivityQueueService._save_sent_activity(activity_b, ScheduledActivity, type='update',
                                                               external_id='https://distant.com/inbox/')

        ActivityQueueService._activity_queue_worker('https://distant.com/inbox/', scheduled_b)

        # assert that both activities were sent
        self.assertEquals(ScheduledActivity.objects.count(), 0)
        self.assertEquals(Activity.objects.count(), 2)

    @override_settings(SEND_BACKLINKS=True, DISABLE_OUTBOX='DEBUG')
    def test_first_update_is_sent(self):
        # no prior activity was sent for this object - should send
        obj = {
            '@type': 'hd:circle',
            '@id': 'https://test.com/circles/8/',
            'owner': {'@id': 'https://distant.com/users/john/',
                      '@type': 'foaf:user'}
        }
        activity = ActivityPubService.build_activity(BACKLINKS_ACTOR, obj, activity_type='Create', summary='A')
        scheduled = ActivityQueueService._save_sent_activity(activity, ScheduledActivity, type='update',
                                                             external_id='https://distant.com/inbox/')
        ActivityQueueService._activity_queue_worker('https://distant.com/inbox/', scheduled)
        self.assertEquals(ScheduledActivity.objects.count(), 0)
        self.assertEquals(Activity.objects.count(), 1)
