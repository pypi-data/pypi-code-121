from datetime import date
from uuid import UUID

import pytest
from freezegun import freeze_time

from microservice_utils import events


@events.register_event
class FakePaymentInitiated(events.Event):
    ...


@events.register_event
class FakePaymentSubmitted(events.Event):
    confirmation_id: UUID
    type: str


@events.register_event
class FakeNotificationSent(events.Event):
    ...


@events.register_event
class FakeReviewPosted(events.Event):
    content: str
    date: date
    permalink: str
    rating: int
    raw_rating: str
    summary: str


@pytest.mark.parametrize(
    "event,expected_event_name",
    [
        (FakePaymentInitiated, "FakePaymentInitiated"),
        (FakeNotificationSent, "FakeNotificationSent"),
        (FakeReviewPosted, "FakeReviewPosted"),
    ],
)
def test_event(event, expected_event_name):
    assert event.name == expected_event_name


@freeze_time("2022-01-19 19:20+00:00")
def test_event_envelope():
    """This test verifies that EventEnvelope creates the correct message schema for
    publishing events as messages via Pub/Sub, etc"""
    event = FakeReviewPosted(
        content="This place is cool",
        date=date(2022, 1, 18),
        permalink="https://fakereviews.com/abc",
        rating=4,
        raw_rating="4",
        summary="Cool place",
    )

    # Create message that can be published and verify
    message = events.EventEnvelope.create(event)

    assert message.event_type == "FakeReviewPosted"
    assert message.timestamp == 1642620000
    assert message.data == event

    # Check publishable json
    # Should look something like this:
    # {"event_type": "FakeReviewPosted", "timestamp": 1642620000,
    # "data": {"content": "This place is cool", etc }}
    publishable = message.to_publishable_json()

    assert isinstance(publishable, bytes)
    assert event.json().encode("utf-8") in publishable


def test_event_envelope_from_published_json():
    """Test reconstituting an EventEnvelope and Event from bytes"""
    raw_received_message = b"""
    {"event_type": "FakePaymentSubmitted", "timestamp": 1642620000, "data":
    {"confirmation_id": "11c6a57c-c2b5-4aca-8676-56b215da28bd", "type": "CC" }}
    """

    expected_event = FakePaymentSubmitted(
        confirmation_id="11c6a57c-c2b5-4aca-8676-56b215da28bd", type="CC"
    )

    message = events.EventEnvelope.from_published_json(raw_received_message)

    assert message.event_type == "FakePaymentSubmitted"
    assert message.timestamp == 1642620000
    assert message.data == expected_event


@pytest.mark.parametrize(
    "payload",
    [
        b"""{"timestamp": 1642620000, "data": {"type": "Something" }}""",
        b"""{"event_type": "FakePaymentSubmitted", "timestamp": 1642620000 }""",
    ],
)
def test_event_envelope_from_published_json_invalid_schema(payload):
    with pytest.raises(RuntimeError):
        events.EventEnvelope.from_published_json(payload)


def test_event_envelope_from_published_json_unknown_event_type():
    raw_received_message = b"""
    {"event_type": "SomethingUnknownHappened", "timestamp": 1642620000, "data":
    {"trace_id": "11c6a57c-c2b5-4aca-8676-56b215da28bd" }}
    """

    with pytest.raises(RuntimeError):
        events.EventEnvelope.from_published_json(raw_received_message)
