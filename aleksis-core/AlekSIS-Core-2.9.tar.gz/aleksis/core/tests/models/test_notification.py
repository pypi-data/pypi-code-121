from datetime import timedelta
from time import sleep
from unittest.mock import patch

from django.test import override_settings
from django.utils import timezone

import pytest
from freezegun import freeze_time

from aleksis.core.models import Notification, Person
from aleksis.core.util.notifications import _send_due_notifications

pytestmark = pytest.mark.django_db


def test_send_notification():
    email = "doe@example.com"
    recipient = Person.objects.create(first_name="Jane", last_name="Doe", email=email)

    sender = "Foo"
    title = "There is happened something."
    description = "Here you get some more information."
    link = "https://aleksis.org/"

    notification = Notification(
        sender=sender,
        recipient=recipient,
        title=title,
        description=description,
        link=link,
    )

    with patch("aleksis.core.models.Notification.send") as patched_send:
        patched_send.assert_not_called()

        notification.save()

        patched_send.assert_called()


def test_send_scheduled_notification():
    email = "doe@example.com"
    recipient = Person.objects.create(first_name="Jane", last_name="Doe", email=email)

    sender = "Foo"
    title = "There is happened something."
    description = "Here you get some more information."
    link = "https://aleksis.org/"

    notification = Notification(
        sender=sender,
        recipient=recipient,
        title=title,
        description=description,
        link=link,
        send_at=timezone.now() + timedelta(days=1),
    )
    notification.save()

    with patch("aleksis.core.models.Notification.send") as patched_send:
        patched_send.assert_not_called()

        _send_due_notifications()

        patched_send.assert_not_called()

        with freeze_time(timezone.now() + timedelta(days=1)):
            _send_due_notifications()

        patched_send.assert_called()


@override_settings(CELERY_BROKER_URL="memory://localhost//")
@pytest.mark.django_db(
    databases=["default", "default_oot"], serialized_rollback=True, transaction=True
)
def test_email_notification(mailoutbox, celery_worker):
    email = "doe@example.com"
    recipient = Person.objects.create(first_name="Jane", last_name="Doe", email=email)

    sender = "Foo"
    title = "There is happened something."
    description = "Here you get some more information."
    link = "https://aleksis.org/"

    notification = Notification(
        sender=sender, recipient=recipient, title=title, description=description, link=link
    )
    notification.save()

    sleep(3)

    notification.refresh_from_db()
    assert notification.sent

    assert len(mailoutbox) == 1

    mail = mailoutbox[0]

    assert email in mail.to
    assert title in mail.body
    assert description in mail.body
    assert link in mail.body
    assert sender in mail.body
    assert recipient.addressing_name in mail.subject
    assert recipient.addressing_name in mail.body
