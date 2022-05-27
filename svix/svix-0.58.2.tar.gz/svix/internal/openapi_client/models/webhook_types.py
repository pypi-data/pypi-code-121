from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.endpoint_created_event import EndpointCreatedEvent
from ..models.endpoint_deleted_event import EndpointDeletedEvent
from ..models.endpoint_disabled_event import EndpointDisabledEvent
from ..models.endpoint_updated_event import EndpointUpdatedEvent
from ..models.message_attempt_exhausted_event import MessageAttemptExhaustedEvent
from ..models.message_attempt_failing_event import MessageAttemptFailingEvent

T = TypeVar("T", bound="WebhookTypes")


@attr.s(auto_attribs=True)
class WebhookTypes:
    """All of the webhook types that we support

    Attributes:
        a (EndpointDisabledEvent): Sent when an endpoint has been automatically disabled after continuous failures.
            Example: {'data': {'appId': 'app_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'appUid': 'unique-app-identifier', 'endpointId':
            'ep_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'failSince': '1970-01-01T00:00:00'}, 'type': 'endpoint.disabled'}.
        a1 (MessageAttemptFailingEvent): Sent after a message has been failing for a few times.
            It's sent on the fourth failure. It complements `message.attempt.exhausted` which is sent after the last
            failure. Example: {'data': {'appId': 'app_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'appUid': 'unique-app-identifier',
            'endpointId': 'ep_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'lastAttempt': {'id': 'atmpt_1srOrx2ZWZBpBUvZwXKQmoEYga2',
            'responseStatusCode': 500, 'timestamp': '1970-01-01T00:00:00'}, 'msgId': 'msg_1srOrx2ZWZBpBUvZwXKQmoEYga2'},
            'type': 'message.attempt.failing'}.
        b (EndpointCreatedEvent): Sent when an endpoint is created. Example: {'data': {'appId':
            'app_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'appUid': 'unique-app-identifier', 'endpointId':
            'ep_1srOrx2ZWZBpBUvZwXKQmoEYga2'}, 'type': 'endpoint.created'}.
        c (EndpointUpdatedEvent): Sent when an endpoint is updated. Example: {'data': {'appId':
            'app_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'appUid': 'unique-app-identifier', 'endpointId':
            'ep_1srOrx2ZWZBpBUvZwXKQmoEYga2'}, 'type': 'endpoint.updated'}.
        d (EndpointDeletedEvent): Sent when an endpoint is deleted. Example: {'data': {'appId':
            'app_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'appUid': 'unique-app-identifier', 'endpointId':
            'ep_1srOrx2ZWZBpBUvZwXKQmoEYga2'}, 'type': 'endpoint.deleted'}.
        e (MessageAttemptExhaustedEvent): Sent when a message delivery has failed (all of the retry attempts have been
            exhausted). Example: {'data': {'appId': 'app_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'appUid': 'unique-app-identifier',
            'endpointId': 'ep_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'lastAttempt': {'id': 'atmpt_1srOrx2ZWZBpBUvZwXKQmoEYga2',
            'responseStatusCode': 500, 'timestamp': '1970-01-01T00:00:00'}, 'msgId': 'msg_1srOrx2ZWZBpBUvZwXKQmoEYga2'},
            'type': 'message.attempt.exhausted'}.
    """

    a: EndpointDisabledEvent
    a1: MessageAttemptFailingEvent
    b: EndpointCreatedEvent
    c: EndpointUpdatedEvent
    d: EndpointDeletedEvent
    e: MessageAttemptExhaustedEvent
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        a = self.a.to_dict()

        a1 = self.a1.to_dict()

        b = self.b.to_dict()

        c = self.c.to_dict()

        d = self.d.to_dict()

        e = self.e.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "a": a,
                "a1": a1,
                "b": b,
                "c": c,
                "d": d,
                "e": e,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        a = EndpointDisabledEvent.from_dict(dict_copy.pop("a"))

        a1 = MessageAttemptFailingEvent.from_dict(dict_copy.pop("a1"))

        b = EndpointCreatedEvent.from_dict(dict_copy.pop("b"))

        c = EndpointUpdatedEvent.from_dict(dict_copy.pop("c"))

        d = EndpointDeletedEvent.from_dict(dict_copy.pop("d"))

        e = MessageAttemptExhaustedEvent.from_dict(dict_copy.pop("e"))

        webhook_types = cls(
            a=a,
            a1=a1,
            b=b,
            c=c,
            d=d,
            e=e,
        )

        webhook_types.additional_properties = dict_copy
        return webhook_types

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
