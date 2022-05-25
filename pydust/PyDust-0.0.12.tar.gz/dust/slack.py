import traceback
import requests
import json

from datetime import datetime
from dust import Datatypes, ValueTypes, Operation, MetaProps, FieldProps
from dust.entity import Store, Entity, _entity_map, get_unit_deps_tuple
from dust.events import get_event, EventType
from dust.messages import register_listener, unregister_listener

UNIT_SLACK = "slack"
UNIT_SLACK_META = "slack_meta"
UNIT_ID = 7
UNIT_META_ID = 8

def get_unit_dependencies():
    return [
        get_unit_deps_tuple("dust.events", "UNIT_EVENTS", "EventTypes")
    ]

class SlackChannelMeta(MetaProps):
    name = (Datatypes.STRING, ValueTypes.SINGLE, 1, 100)
    webhook_url = (Datatypes.STRING, ValueTypes.SINGLE, 2, 101)
    test_webhook_url = (Datatypes.STRING, ValueTypes.SINGLE, 3, 102)

class SlackNotificationMeta(MetaProps):
    notification = (Datatypes.STRING, ValueTypes.SINGLE, 1, 200)
    channel = (Datatypes.ENTITY, ValueTypes.SINGLE, 2, 201)
    report_time = (Datatypes.ENTITY, ValueTypes.SINGLE, 3, 202)
    sent = (Datatypes.BOOL, ValueTypes.SINGLE, 4, 203)
    test = (Datatypes.BOOL, ValueTypes.SINGLE, 4, 204)

class SlackTypes(FieldProps):
    channel = (UNIT_SLACK_META, SlackChannelMeta, 1)
    notification = (UNIT_SLACK_META, SlackNotificationMeta, 2)

Store.create_unit(UNIT_SLACK, UNIT_ID)
Store.load_types_from_enum(SlackTypes, UNIT_META_ID)

_channels = {}

def _default_event_filter(message_type, message_params, entities):
    for global_id in entities:
        entity = Store.access(Operation.GET, None, global_id)

        if message_params["op"] == Operation.SET.name and \
           entity.get_meta_type_enum() == SlackTypes.notification and \
           not entity.access(Operation.GET, None, SlackNotificationMeta.notification) is None and \
           not entity.access(Operation.GET, None, SlackNotificationMeta.channel) is None and \
           not entity.access(Operation.GET, None, SlackNotificationMeta.report_time) is None and \
           not entity.access(Operation.GET, None, SlackNotificationMeta.test) is None and \
           not entity.access(Operation.GET, False, SlackNotificationMeta.sent):
            return True

    return False


def register_slack_listener(channel_name, event_filter=_default_event_filter):
    register_listener("{}:{}".format(UNIT_SLACK, channel_name), event_filter, _notify_slack)

def unregister_slack_listener(channel_name):
    unregister_listener("{}:{}".format(UNIT_SLACK, channel_name))

def register_channel(channel_name, webhook_url, test_webhook_url=None, register_default_listener=True):
    if test_webhook_url is None:
        test_webhook_url = webhook_url

    channel = Store.access(Operation.GET, None, UNIT_SLACK, None, SlackTypes.channel)
    channel.access(Operation.SET, channel_name, SlackChannelMeta.name)
    channel.access(Operation.SET, webhook_url, SlackChannelMeta.webhook_url)
    channel.access(Operation.SET, test_webhook_url, SlackChannelMeta.test_webhook_url)

    _channels[channel_name] = channel
    if register_default_listener:
        register_slack_listener(channel_name)


def _notify_slack(message_type, message_params, entities):
    print(str(entities))
    for global_id in entities:
        entity = Store.access(Operation.GET, None, global_id)
        notification = entity.access(Operation.GET, None, SlackNotificationMeta.notification)

        if notification and len(notification.strip()) > 0:
            webhook_url = None
            if entity.access(Operation.GET, True, SlackNotificationMeta.test):
                webhook_url = entity.access(Operation.GET, None, SlackNotificationMeta.channel, SlackChannelMeta.test_webhook_url)
            else:
                webhook_url = entity.access(Operation.GET, None, SlackNotificationMeta.channel, SlackChannelMeta.webhook_url)

            print("Sending to slack")
            response = requests.post(
                webhook_url, data = json.dumps({'text': notification}),
                headers={'Content-Type': 'application/json'}
                )
            if response.status_code != 200:
                raise ValueError(
                    'Request to slack returned an error %s, the response is:\n%s'
                    % (response.status_code, response.text)
                    )

def create_slack_notification(channel_name, notification, test=True):
    if notification and len(notification.strip()) > 0:
        notif_entity = Store.access(Operation.GET, None, UNIT_SLACK, None, SlackTypes.notification)
        notif_entity.access(Operation.SET, notification, SlackNotificationMeta.notification)
        notif_entity.access(Operation.SET, _channels[channel_name], SlackNotificationMeta.channel)
        notif_entity.access(Operation.SET, get_event(datetime.now(), EventType.DATETIME), SlackNotificationMeta.report_time)
        notif_entity.access(Operation.SET, False, SlackNotificationMeta.sent)
        notif_entity.access(Operation.SET, test, SlackNotificationMeta.test)

        return notif_entity

    return None
