import threading
import json
import time
import requests
from queue import Queue
from requests.exceptions import Timeout, ConnectionError
from urllib.parse import urlparse
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver, Signal
from django.conf import settings
from rest_framework.utils import model_meta

from djangoldp.models import Model, Follower, ScheduledActivity
from djangoldp.models import Activity as ActivityModel

import logging


logger = logging.getLogger('djangoldp')
BACKLINKS_ACTOR = {
    "type": "Service",
    "name": "Backlinks Service"
}

SCHEDULER_SETTINGS = {
    'apscheduler.timezone': getattr(settings, 'TIME_ZONE', 'UTC'),
}

MAX_ACTIVITY_RESCHEDULES = getattr(settings, 'MAX_ACTIVITY_RESCHEDULES', 3)
DEFAULT_BACKOFF_FACTOR = getattr(settings, 'DEFAULT_BACKOFF_FACTOR', 1)
DEFAULT_ACTIVITY_DELAY = getattr(settings, 'DEFAULT_ACTIVITY_DELAY', 0.1)
DEFAULT_REQUEST_TIMEOUT = getattr(settings, 'DEFAULT_REQUEST_TIMEOUT', 10)


activity_sending_finished = Signal()


class ActivityQueueService:
    '''Manages an asynchronous queue for Activity format messages'''
    initialized = False
    queue = None

    @classmethod
    def revive_activities(cls):
        '''re-schedules all ScheduledActivities to the queue'''
        with cls.queue.mutex:
            cls.queue.queue.clear()

        scheduled = ScheduledActivity.objects.all()
        for activity in scheduled:
            if activity.external_id is not None:
                cls.resend_activity(str(activity.external_id), activity, failed=False)
            else:
                activity.delete()

    @classmethod
    def start(cls):
        '''
        method checks if there are scheduled activities on the queue and starts them up
        Important: this method should only be called in start-up, when you know there are not queue tasks running
        otherwise duplicate activities may be sent
        '''
        def queue_worker(queue):
            while True:
                # wait for queue item to manifest
                item = queue.get()
                time.sleep(item[2])
                cls._activity_queue_worker(item[0], item[1])
                cls.queue.task_done()

        if not cls.initialized:
            cls.initialized = True

            # initialise the queue worker - infinite maxsize
            cls.queue = Queue(maxsize=0)
            t = threading.Thread(target=queue_worker, args=[cls.queue])
            t.setDaemon(True)
            t.start()

            cls.revive_activities()

    @classmethod
    def do_post(cls, url, activity, auth=None, timeout=DEFAULT_REQUEST_TIMEOUT):
        '''
        makes a POST request to url, passing activity
        :returns: response from server
        :raises: Timeout or ConnectionError if the post could not be made
        '''
        headers = {'Content-Type': 'application/ld+json'}
        logger.debug('[Sender] sending Activity... ' + str(activity))

        if getattr(settings, 'DISABLE_OUTBOX', False) == 'DEBUG':
            return {'data': {}}
        return requests.post(url, data=json.dumps(activity), headers=headers, timeout=timeout)

    @classmethod
    def _save_activity_from_response(cls, response, url, scheduled_activity):
        '''
        wrapper to save a finished Activity based on the parameterised response
        :return: saved Activity object
        '''
        response_body = None

        if hasattr(response, 'text'):
            response_body = response.text
        response_location = getattr(response, "Location", None)
        status_code = getattr(response, "status_code", None)
        success = str(status_code).startswith("2")

        return cls._save_sent_activity(scheduled_activity.to_activitystream(), ActivityModel, success=success,
                                       external_id=url, type=scheduled_activity.type,
                                       response_location=response_location, response_code=str(status_code),
                                       response_body=response_body)

    @classmethod
    def _attempt_failed_reschedule(cls, url, scheduled_activity, backoff_factor):
        '''
        either re-schedules a failed activity or saves its failure state, depending on the number of fails and the
        fail policy (MAX_ACTIVITY_RESCHEDULES)
        :return: True if it was able to reschedule
        '''
        if scheduled_activity.failed_attempts < MAX_ACTIVITY_RESCHEDULES:
            backoff = backoff_factor * (2 ** (scheduled_activity.failed_attempts - 1))
            cls.resend_activity(url, scheduled_activity, backoff)
            return True

        # no retries left, save the failure state
        logger.error('Failed to deliver backlink to ' + str(url) + ' after retrying ' +
                     str(MAX_ACTIVITY_RESCHEDULES) + ' times')

        cls._save_sent_activity(scheduled_activity.to_activitystream(), ActivityModel, success=False, external_id=url,
                                type=scheduled_activity.type, response_code='408')
        return False

    @classmethod
    def _dispatch_activity_sending_finished(cls, response, saved_activity):
        '''sends a 'activity_sending_finished' signal to receivers'''
        activity_sending_finished.send(sender=cls, response=response, saved_activity=saved_activity)

    @classmethod
    def _send_activity(cls, url, scheduled_activity, auth=None, backoff_factor=DEFAULT_BACKOFF_FACTOR):
        '''
        makes a POST request to url, passing ScheduledActivity instance. reschedules if needed
        :param backoff_factor: a factor to use in the extension of waiting for retries. Used both in the RetryStrategy
        of requests.post and in rescheduling an activity which timed out
        '''
        response = None
        activity = scheduled_activity.to_activitystream()
        try:
            response = cls.do_post(url, activity, auth)
        except (Timeout, ConnectionError):
            if cls._attempt_failed_reschedule(url, scheduled_activity, backoff_factor):
                # successfully rescheduled, so skip cleanup for now
                return
        except Exception as e:
            logger.error('Failed to deliver backlink to ' + str(url) + ', was attempting ' + str(activity) +
                         str(e.__class__) + ': ' + str(e))

        saved = None
        if response is not None:
            saved = cls._save_activity_from_response(response, url, scheduled_activity)
        scheduled_activity.delete()

        # emit activity finished event
        cls._dispatch_activity_sending_finished(response, saved)

    @classmethod
    def _activity_queue_worker(cls, url, scheduled_activity):
        '''
        Worker for sending a scheduled activity on the queue. Decides whether to send the activity and then passes to
        _send_activity if it is worth it
        '''

        def get_related_activities(type):
            '''returns a list of activity types which should be considered a "match" with the parameterised type'''
            if type is None:
                return []
            type = type.lower()
            group_a = ['create', 'update', 'delete', 'creation', 'deletion']
            groub_b = ['add', 'remove']

            if type in group_a:
                return group_a
            if type in groub_b:
                return groub_b
            return []

        types = get_related_activities(scheduled_activity.type)
        if len(types) > 0:
            scheduled = ScheduledActivity.objects.filter(external_id=scheduled_activity.external_id,
                                                         created_at__gt=scheduled_activity.created_at,
                                                         type__in=types)

            # filter to scheduled activities on the same object
            scheduled = [s for s in scheduled if cls._is_same_object_target(s, scheduled_activity)]

            if len(scheduled) > 0:
                scheduled_activity.delete()
                return

        if scheduled_activity.type == 'update' and not cls._update_is_new(url, scheduled_activity):
            scheduled_activity.delete()
            return

        if scheduled_activity.type in ['add', 'remove'] and not cls._add_remove_is_new(url, scheduled_activity):
            scheduled_activity.delete()
            return

        cls._send_activity(url, scheduled_activity)

    @classmethod
    def _is_same_object_target(cls, activity_a, activity_b):
        def get_property(object, property, default=None):
            ret = object.get(property, default)
            if isinstance(ret, dict):
                ret = ret.get('@id', ret.get('name', None))
            return ret

        a = activity_a.to_activitystream()
        b = activity_b.to_activitystream()

        if get_property(a, 'object') != get_property(b, 'object'):
            return False

        return get_property(a, 'target', a.get('origin', None)) == get_property(b, 'target', b.get('origin', None))

    @classmethod
    def _update_is_new(cls, url, scheduled_activity):
        '''auxiliary function which validates if a scheduled update holds new information, compared to a past success'''
        def ordered(obj):
            '''recursively sorts nested dictionary objects to standardise ordering in comparison'''
            if isinstance(obj, dict):
                return sorted((k, ordered(v)) for k, v in obj.items())
            else:
                return obj

        def no_new_changes(old_activity, new_activity):
            '''returns False if the two activities are equivalent'''
            return ordered(old_activity['object']) == ordered(new_activity['object'])

        def get_most_recent_sent_activity(external_id):
            '''returns the most recently sent activity which meets the specification'''
            activities = ActivityModel.objects.filter(external_id=external_id, is_finished=True,
                                                      type__in=['create', 'update']).order_by('-created_at')[:10]
            for a in activities.all():
                a = a.to_activitystream()
                if 'object' in a:
                    return a
            return None

        # str objects will have to be checked manually by the receiver
        new_activity = scheduled_activity.to_activitystream()
        if 'object' not in new_activity or isinstance(new_activity['object'], str):
            return True

        old_activity = get_most_recent_sent_activity(url)

        if old_activity is None:
            return True

        if no_new_changes(old_activity, new_activity):
            return False
        return True

    @classmethod
    def _add_remove_is_new(cls, url, scheduled_activity):
        '''auxiliary function validates if the receiver does not know about this Add/Remove activity'''
        def get_most_recent_sent_activity(source_obj, source_target_origin):
            # get a list of activities with the right type
            activities = ActivityModel.objects.filter(external_id=url, is_finished=True,
                                                      type__in=['add', 'remove']).order_by('-created_at')[:10]

            # we are searching for the most recent Add/Remove activity which shares inbox, object and target/origin
            for a in activities.all():
                astream = a.to_activitystream()
                obj = astream.get('object', None)
                target_origin = astream.get('target', astream.get('origin', None))
                if obj is None or target_origin is None:
                    continue

                if source_obj == obj and source_target_origin == target_origin:
                    return a
            return None

        new_activity = scheduled_activity.to_activitystream()
        new_obj = new_activity.get('object', None)
        new_target_origin = new_activity.get('target', new_activity.get('origin', None))

        # bounds checking
        if new_obj is None or new_target_origin is None:
            return True

        #  if most recent is the same type of activity as me, it's not new
        old_activity = get_most_recent_sent_activity(new_obj, new_target_origin)
        if old_activity is not None and old_activity.type == scheduled_activity.type:
            return False
        return True

    @classmethod
    def _push_to_queue(cls, url, scheduled_activity, delay=DEFAULT_ACTIVITY_DELAY):
        '''wrapper to check for singleton initialization before pushing'''
        if not cls.initialized:
            cls.start()
        cls.queue.put([url, scheduled_activity, delay])

    @classmethod
    def resend_activity(cls, url, scheduled_activity, failed=True):
        '''
        a variation of send_activity for ScheduledActivity objects
        :param url: the recipient url inbox
        :param scheduled_activity: a ScheduledActivity object for sending
        :param failed: set to True to increment scheduled_activity.failed_attempts, to keep track of the number of resends
        '''
        if failed:
            scheduled_activity.failed_attempts = scheduled_activity.failed_attempts + 1
            scheduled_activity.save()

        cls._push_to_queue(url, scheduled_activity)

    @classmethod
    def send_activity(cls, url, activity, auth=None, delay=DEFAULT_ACTIVITY_DELAY):
        '''
        saves a ScheduledActivity for the parameterised activity and passes it to the queue
        :param url: the recipient url inbox
        :param activity: an Activity to send
        '''
        if getattr(settings, 'DISABLE_OUTBOX', False) is not False:
            if getattr(settings, 'DISABLE_OUTBOX') == 'DEBUG':
                cls._save_sent_activity(activity, ActivityModel, external_id=url, success=True, type=activity.get('type', None),
                                        response_code='201')
            return

        # schedule the activity
        scheduled = cls._save_sent_activity(activity, ScheduledActivity, external_id=url, type=activity.get('type', None))
        cls._push_to_queue(url, scheduled, delay)

    @classmethod
    def _save_sent_activity(cls, activity, model_represenation=ActivityModel, success=False, external_id=None, type=None,
                            response_location=None, response_code=None, local_id=None, response_body=None):
        '''
        Auxiliary function saves a record of parameterised activity
        :param model_represenation: the model class which should be used to store the activity. Defaults to djangol.Activity, must be a subclass
        '''
        payload = bytes(json.dumps(activity), "utf-8")
        if response_body is not None:
            response_body = bytes(json.dumps(response_body), "utf-8")
        if local_id is None:
            local_id = settings.SITE_URL + "/outbox/"
        if type is not None:
            type = type.lower()
        elif 'type' in activity and isinstance(activity.get('type'), str):
            type = activity.get('type').lower()
        obj = model_represenation.objects.create(local_id=local_id, payload=payload, success=success,
                                                 external_id=external_id, type=type, response_location=response_location,
                                                 response_code=response_code, response_body=response_body)
        return obj


class ActivityPubService(object):
    '''A service aiding the construction and sending of ActivityStreams notifications'''

    @classmethod
    def build_object_tree(cls, instance):
        '''builds a depth 1 object tree from a parameterised instance, with each branch being an object's urlid and RDF type'''
        model = type(instance)
        info = model_meta.get_field_info(model)

        if not hasattr(instance, 'urlid'):
            return

        obj = {
            "@type": Model.get_model_rdf_type(model),
            "@id": instance.urlid
        }
        if obj['@type'] is None:
            return

        # append relations
        for field_name, relation_info in info.relations.items():
            if not relation_info.to_many:
                value = getattr(instance, field_name, None)
                if value is None:
                    continue

                sub_object = {
                    "@id": value.urlid,
                    "@type": Model.get_model_rdf_type(type(value))
                }

                if sub_object['@type'] is None:
                    continue

                obj[field_name] = sub_object

        return obj

    @classmethod
    def get_actor_from_user_instance(cls, user):
        '''Auxiliary function returns valid Actor object from parameterised user instance, None if parameter invalid'''
        if isinstance(user, get_user_model()) and hasattr(user, 'urlid'):
            return {
                '@type': 'foaf:user',
                '@id': user.urlid
            }
        return None

    @classmethod
    def discover_inbox(cls, target_id):
        '''a method which discovers the inbox of the target resource'''
        url = urlparse(target_id)
        return target_id.replace(url.path, "/") + "inbox/"

    @classmethod
    def build_activity(self, actor, obj, activity_type='Activity', **kwargs):
        '''Auxiliary function returns an activity object with kwargs in the body'''
        res = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                settings.LDP_RDF_CONTEXT
            ],
            "type": activity_type,
            "actor": actor,
            "object": obj
        }

        for kwarg in kwargs:
            res.update({kwarg: kwargs[kwarg]})

        return res

    @classmethod
    def send_add_activity(cls, actor, obj, target):
        '''
        Sends an Add activity
        :param actor: a valid Actor object
        :param obj: a valid ActivityStreams Object
        :param target: an object representing the target collection
        '''
        summary = str(obj['@id']) + " was added to " + str(target['@id'])
        activity = cls.build_activity(actor, obj, activity_type='Add', summary=summary, target=target)

        # send request
        inbox = ActivityPubService.discover_inbox(target['@id'])
        ActivityQueueService.send_activity(inbox, activity)

    @classmethod
    def send_remove_activity(cls, actor, obj, origin):
        '''
        Sends a Remove activity
        :param actor: a valid Actor object, or a user instance
        :param obj: a valid ActivityStreams Object
        :param origin: the context the object has been removed from
        '''
        summary = str(obj['@id']) + " was removed from " + str(origin['@id'])
        activity = cls.build_activity(actor, obj, activity_type='Remove', summary=summary, origin=origin)

        # send request
        inbox = ActivityPubService.discover_inbox(origin['@id'])
        ActivityQueueService.send_activity(inbox, activity)

    @classmethod
    def send_create_activity(cls, actor, obj, inbox):
        '''
        Sends a Create activity
        :param actor: a valid Actor object, or a user instance
        :param obj: a valid ActivityStreams Object
        :param inbox: the inbox to send the activity to
        '''
        summary = str(obj['@id']) + " was created"
        activity = cls.build_activity(actor, obj, activity_type='Create', summary=summary)

        ActivityQueueService.send_activity(inbox, activity)

    @classmethod
    def send_update_activity(cls, actor, obj, inbox):
        '''
        Sends an Update activity
        :param actor: a valid Actor object, or a user instance
        :param obj: a valid ActivityStreams Object
        :param inbox: the inbox to send the activity to
        '''
        summary = str(obj['@id']) + " was updated"
        activity = cls.build_activity(actor, obj, activity_type='Update', summary=summary)

        ActivityQueueService.send_activity(inbox, activity)

    @classmethod
    def send_delete_activity(cls, actor, obj, inbox):
        '''
        Sends a Remove activity
        :param actor: a valid Actor object, or a user instance
        :param obj: a valid ActivityStreams Object
        :param inbox: the inbox to send the activity to
        '''
        summary = str(obj['@id']) + " was deleted"
        activity = cls.build_activity(actor, obj, activity_type='Delete', summary=summary)

        ActivityQueueService.send_activity(inbox, activity)

    @classmethod
    def get_related_externals(cls, sender, instance):
        '''Auxiliary function returns a set of urlids of distant resources connected to paramertised instance'''
        info = model_meta.get_field_info(sender)

        # bounds checking
        if not hasattr(instance, 'urlid') or Model.get_model_rdf_type(sender) is None:
            return set()

        # check each foreign key for a distant resource
        targets = set()
        for field_name, relation_info in info.relations.items():
            if not relation_info.to_many:
                value = getattr(instance, field_name, None)
                if value is not None and Model.is_external(value):
                    target_type = Model.get_model_rdf_type(type(value))

                    if target_type is None:
                        continue

                    targets.add(value.urlid)

        return targets

    @classmethod
    def get_target_inboxes(cls, urlids):
        '''Auxiliary function returns a set of inboxes, from a set of target object urlids'''
        inboxes = set()
        for urlid in urlids:
            inboxes.add(ActivityPubService.discover_inbox(urlid))
        return inboxes

    @classmethod
    def get_follower_inboxes(cls, object_urlid):
        '''Auxiliary function returns a set of inboxes, from the followers of parameterised object urlid'''
        inboxes = set(Follower.objects.filter(object=object_urlid).values_list('inbox', flat=True))
        return inboxes

    @classmethod
    def save_follower_for_target(cls, external_urlid, obj_id):
        inbox = ActivityPubService.discover_inbox(external_urlid)

        if not Follower.objects.filter(object=obj_id, follower=external_urlid).exists():
            Follower.objects.create(object=obj_id, inbox=inbox, follower=external_urlid,
                                    is_backlink=True)

    @classmethod
    def save_followers_for_targets(cls, external_urlids, obj_id):
        '''
        saves Follower objects for any external urlid which isn't already following the object in question
        :param external_urlids: list of external urlids to populate the follower inbox
        :param obj_id: object id to be followed
        '''
        existing_followers = Follower.objects.filter(object=obj_id).values_list('follower', flat=True)
        for urlid in external_urlids:
            if urlid not in existing_followers:
                Follower.objects.create(object=obj_id, inbox=ActivityPubService.discover_inbox(urlid),
                                        follower=urlid, is_backlink=True)

    @classmethod
    def remove_followers_for_resource(cls, external_urlid, obj_id):
        '''removes all followers which match the follower urlid, obj urlid combination'''
        inbox = ActivityPubService.discover_inbox(external_urlid)

        for follower in Follower.objects.filter(object=obj_id, follower=external_urlid,
                                                inbox=inbox, is_backlink=True):
            follower.delete()


@receiver([post_save])
def check_save_for_backlinks(sender, instance, created, **kwargs):
    if getattr(settings, 'SEND_BACKLINKS', True) and getattr(instance, 'allow_create_backlink', False) \
            and not Model.is_external(instance) \
            and getattr(instance, 'username', None) != 'hubl-workaround-493':
        external_urlids = ActivityPubService.get_related_externals(sender, instance)
        inboxes = ActivityPubService.get_follower_inboxes(instance.urlid)
        targets = set().union(ActivityPubService.get_target_inboxes(external_urlids), inboxes)

        if len(targets) > 0:
            obj = ActivityPubService.build_object_tree(instance)
            actor = BACKLINKS_ACTOR
            # Create Activity
            if created:
                for target in targets:
                    ActivityPubService.send_create_activity(actor, obj, target)
            # Update Activity
            else:
                for target in targets:
                    ActivityPubService.send_update_activity(actor, obj, target)

            # create Followers to update external resources of changes in future
            ActivityPubService.save_followers_for_targets(external_urlids, obj['@id'])


@receiver([post_delete])
def check_delete_for_backlinks(sender, instance, **kwargs):
    if getattr(settings, 'SEND_BACKLINKS', True) and getattr(instance, 'allow_create_backlink', False) \
            and getattr(instance, 'username', None) != 'hubl-workaround-493':
        targets = ActivityPubService.get_follower_inboxes(instance.urlid)

        if len(targets) > 0:
            for target in targets:
                ActivityPubService.send_delete_activity(BACKLINKS_ACTOR, {
                    "@id": instance.urlid,
                    "@type": Model.get_model_rdf_type(sender)
                }, target)

    # remove any Followers on this resource
    urlid = getattr(instance, 'urlid', None)
    if urlid is not None:
        for follower in Follower.objects.filter(object=urlid):
            follower.delete()


@receiver([m2m_changed])
def check_m2m_for_backlinks(sender, instance, action, *args, **kwargs):
    def build_targets(query_set):
        '''analyses parameterised queryset (removed or added members) for backlinks'''
        targets = []

        for obj in query_set:
            condition = Model.is_external(obj) and getattr(obj, 'allow_create_backlink', False)
            if action == "post_add":
                condition = condition and not getattr(obj, 'is_backlink', True)

            if condition:
                targets.append({
                    "@type": member_rdf_type,
                    "@id": obj.urlid
                })

        return targets

    if getattr(settings, 'SEND_BACKLINKS', True):
        member_model = kwargs['model']
        pk_set = kwargs['pk_set']

        # we can only send backlinks on pre_clear because on post_clear the objects are gone
        if action != "pre_clear" and pk_set is None:
            return
        member_rdf_type = Model.get_model_rdf_type(member_model)
        container_rdf_type = Model.get_model_rdf_type(type(instance))

        if member_rdf_type is None:
            return
        if container_rdf_type is None:
            return

        # build list of targets (models affected by the change)
        if action == "pre_clear":
            sender_info = model_meta.get_field_info(sender)
            for field_name, relation_info in sender_info.relations.items():
                if relation_info.related_model == member_model:
                    pk_set = sender.objects.all().values_list(field_name, flat=True)
        if pk_set is None or len(pk_set) == 0:
            return
        query_set = member_model.objects.filter(pk__in=pk_set)
        targets = build_targets(query_set)

        if len(targets) > 0:
            obj = {
                "@type": container_rdf_type,
                "@id": instance.urlid
            }
            if action == 'post_add':
                for target in targets:
                    ActivityPubService.send_add_activity(BACKLINKS_ACTOR, obj, target)
                    ActivityPubService.save_follower_for_target(target['@id'], obj['@id'])

            elif action == "post_remove" or action == "pre_clear":
                for target in targets:
                    ActivityPubService.send_remove_activity(BACKLINKS_ACTOR, obj, target)
                    ActivityPubService.remove_followers_for_resource(target['@id'], obj['@id'])
