import json
from django import forms
from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import gettext_noop, ugettext_lazy as _
from i18nfield.strings import LazyI18nString
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import (
    logentry_display,
    order_canceled,
    order_expired,
    order_modified,
    order_placed,
)
from pretix.base.templatetags.rich_text import rich_text_snippet
from pretix.control.signals import nav_event_settings
from pretix.presale.signals import question_form_fields

from .tasks import matrix_inviter_invite, matrix_inviter_kick

settings_hierarkey.add_default("matrix_inviter_items", [], list)
settings_hierarkey.add_default("matrix_inviter_authorization_token", "", str)
settings_hierarkey.add_default("matrix_inviter_matrix_server", "", str)
settings_hierarkey.add_default("matrix_inviter_matrix_room", "", str)
settings_hierarkey.add_default(
    "matrix_inviter_hint",
    LazyI18nString.from_gettext(
        gettext_noop("You will be invited to the event's Matrix Space.")
    ),
    LazyI18nString,
)
settings_hierarkey.add_default(
    "matrix_inviter_reason",
    "",
    LazyI18nString,
)


@receiver(question_form_fields, dispatch_uid="matrix_inviter_questions")
def add_matrix_id_question(sender, position, **kwargs):
    if str(position.item.pk) not in sender.settings.get("matrix_inviter_items"):
        return {}

    if (
        not sender.settings.matrix_inviter_authorization_token
        and not sender.settings.matrix_inviter_matrix_server
        and not sender.settings.matrix_inviter_matrix_room
    ):
        return {}

    return {
        "matrix_inviter_matrix_id": forms.RegexField(
            label=_("Matrix ID"),
            required=False,
            regex="@[a-z0-9._=/-]+:[a-z0-9.-]+",
            strip=True,
            error_messages={
                "invalid": _("Enter a Matrix ID of the form @username:homeserver.tld")
            },
            help_text=rich_text_snippet(sender.settings.matrix_inviter_hint),
        )
    }


@receiver(order_placed, dispatch_uid="matrix_inviter_order_placed")
@receiver(order_modified, dispatch_uid="matrix_inviter_order_modified")
def matrix_inviter_invite_async(sender, order, **kwargs):
    if (
        not sender.settings.matrix_inviter_authorization_token
        and not sender.settings.matrix_inviter_matrix_server
        and not sender.settings.matrix_inviter_matrix_room
    ):
        return

    for order_position in order.positions.all():
        if str(order_position.item.pk) not in sender.settings.get(
            "matrix_inviter_items"
        ):
            continue

        if not order_position.meta_info_data.get("question_form_data", {}).get(
            "matrix_inviter_matrix_id"
        ):
            continue

        matrix_inviter_invite.apply_async(
            args=(
                sender.pk,
                order.pk,
                order_position.pk,
                str(sender.settings.matrix_inviter_reason),
            )
        )


@receiver(order_canceled, dispatch_uid="matrix_inviter_order_canceled")
@receiver(order_expired, dispatch_uid="matrix_inviter_order_expired")
def matrix_inviter_kick_async(sender, order, **kwargs):
    if (
        not sender.settings.matrix_inviter_authorization_token
        and not sender.settings.matrix_inviter_matrix_server
        and not sender.settings.matrix_inviter_matrix_room
    ):
        return

    for order_position in order.positions.all():
        if str(order_position.item.pk) not in sender.settings.get(
            "matrix_inviter_items"
        ):
            continue

        if not order_position.meta_info_data.get("question_form_data", {}).get(
            "matrix_inviter_matrix_id"
        ):
            continue

        matrix_inviter_kick.apply_async(
            args=(
                sender.pk,
                order.pk,
                order_position.pk,
            )
        )


@receiver(nav_event_settings, dispatch_uid="matrix_inviter_nav_settings")
def navbar_settings(sender, request=None, **kwargs):
    url = resolve(request.path_info)
    return [
        {
            "label": _("Matrix inviter"),
            "url": reverse(
                "plugins:pretix_matrix_inviter:settings",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "active": url.namespace == "plugins:pretix_matrix_inviter"
            and url.url_name == "settings",
        }
    ]


@receiver(logentry_display, dispatch_uid="matrix_inviter_logentry_display")
def logentry_display(sender, logentry, **kwargs):
    if not logentry.action_type.startswith("pretix_matrix_inviter"):
        return

    locales = {
        "pretix_matrix_inviter.invite_sent": _(
            "{matrix_id} has been invited to {matrix_room}."
        ),
        "pretix_matrix_inviter.invite_rescinded": _(
            "{matrix_id} has been removed from {matrix_room}."
        ),
        "pretix_matrix_inviter.error": _(
            "There was an error inviting {matrix_id} to {matrix_room}: {error}"
        ),
        "pretix_matrix_inviter.remove_error": _(
            "There was an error removing {matrix_id} from {matrix_room}: {error}"
        ),
    }
    data = json.loads(logentry.data)

    return locales[logentry.action_type].format_map(data)
