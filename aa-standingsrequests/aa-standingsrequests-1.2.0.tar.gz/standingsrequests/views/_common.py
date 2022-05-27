from django.db import models
from django.utils.html import format_html

from allianceauth.eveonline.models import EveCharacter

from standingsrequests import __title__
from standingsrequests.constants import DATETIME_FORMAT_HTML
from standingsrequests.core import BaseConfig, ContactType
from standingsrequests.helpers.evecharacter import EveCharacterHelper
from standingsrequests.helpers.evecorporation import EveCorporation
from standingsrequests.models import ContactSet, StandingRequest, StandingRevocation

DEFAULT_ICON_SIZE = 32


def label_with_icon(icon_url: str, text: str):
    return format_html(
        '<span class="text-nowrap">'
        '<img src="{}" class="img-circle" style="width:{}px;height:{}px"> {}'
        "</span>",
        icon_url,
        DEFAULT_ICON_SIZE,
        DEFAULT_ICON_SIZE,
        text,
    )


def add_common_context(request, context: dict) -> dict:
    """adds the common context used by all view"""
    new_context = {
        **{
            "app_title": __title__,
            "operation_mode": str(BaseConfig.operation_mode),
            "pending_total_count": (
                StandingRequest.objects.pending_requests().count()
                + StandingRevocation.objects.pending_requests().count()
            ),
            "DATETIME_FORMAT_HTML": DATETIME_FORMAT_HTML,
        },
        **context,
    }
    return new_context


def compose_standing_requests_data(
    requests_qs: models.QuerySet, quick_check: bool = False
) -> list:
    """composes list of standings requests or revocations based on queryset
    and returns it
    """
    requests_qs = requests_qs.select_related(
        "user", "user__profile__state", "user__profile__main_character"
    )
    # preload data in bulk
    eve_characters = {
        character.character_id: character
        for character in EveCharacter.objects.filter(
            character_id__in=(
                requests_qs.exclude(
                    contact_type_id=ContactType.corporation_id
                ).values_list("contact_id", flat=True)
            )
        )
    }
    # TODO: remove EveCorporation usage
    eve_corporations = {
        corporation.corporation_id: corporation
        for corporation in EveCorporation.get_many_by_id(
            requests_qs.filter(contact_type_id=ContactType.corporation_id).values_list(
                "contact_id", flat=True
            )
        )
    }
    contacts = _identify_contacts(eve_characters, eve_corporations)
    requests_data = list()
    for req in requests_qs:
        (
            main_character_name,
            main_character_ticker,
            main_character_icon_url,
            main_character_html,
            state_name,
        ) = _identify_main(req)

        (
            contact_name,
            contact_icon_url,
            corporation_id,
            corporation_name,
            corporation_ticker,
            alliance_id,
            alliance_name,
            has_scopes,
        ) = _identify_organization(quick_check, eve_characters, eve_corporations, req)

        if contact_name:
            contact_name_html = label_with_icon(contact_icon_url, contact_name)
        else:
            contact_name_html = ""
        if corporation_name:
            organization_html = f"[{corporation_ticker}] {corporation_name}"
            if alliance_name:
                organization_html = format_html(
                    "{}<br>{}", organization_html, alliance_name
                )
        else:
            organization_html = ""

        reason = req.get_reason_display() if req.is_standing_revocation else None
        labels = _fetch_labels(contacts, req)
        requests_data.append(
            {
                "contact_id": req.contact_id,
                "contact_name": contact_name,
                "contact_icon_url": contact_icon_url,
                "contact_name_html": {
                    "display": contact_name_html,
                    "sort": contact_name,
                },
                "corporation_id": corporation_id,
                "corporation_name": corporation_name,
                "corporation_ticker": corporation_ticker,
                "alliance_id": alliance_id,
                "alliance_name": alliance_name,
                "organization_html": organization_html,
                "request_date": req.request_date,
                "action_date": req.action_date,
                "has_scopes": has_scopes,
                "state": state_name,
                "reason": reason,
                "labels": sorted(labels),
                "main_character_name": main_character_name,
                "main_character_ticker": main_character_ticker,
                "main_character_icon_url": main_character_icon_url,
                "main_character_html": main_character_html,
                "actioned": req.is_actioned,
                "is_effective": req.is_effective,
                "is_corporation": req.is_corporation,
                "is_character": req.is_character,
                "action_by": req.action_by.username if req.action_by else "(System)",
            }
        )
    return requests_data


def _identify_contacts(eve_characters, eve_corporations):
    try:
        contact_set = ContactSet.objects.latest()
    except ContactSet.DoesNotExist:
        contacts = dict()
    else:
        all_contact_ids = set(eve_characters.keys()) | set(eve_corporations.keys())
        contacts = {
            obj.eve_entity_id: obj
            for obj in contact_set.contacts.prefetch_related("labels").filter(
                eve_entity_id__in=all_contact_ids
            )
        }
    return contacts


def _identify_main(req):
    main_character_name = main_character_ticker = main_character_icon_url = "-"
    main_character_html = "-"
    if req.user:
        state_name = req.user.profile.state.name
        main = req.user.profile.main_character
        if main:
            main_character_name = main.character_name
            main_character_ticker = main.corporation_ticker
            main_character_icon_url = main.portrait_url(DEFAULT_ICON_SIZE)
            main_character_html = label_with_icon(
                main_character_icon_url,
                f"[{main_character_ticker}] {main_character_name}",
            )
    else:
        state_name = "-"
    return (
        main_character_name,
        main_character_ticker,
        main_character_icon_url,
        main_character_html,
        state_name,
    )


def _identify_organization(quick_check, eve_characters, eve_corporations, req):
    if req.is_character:
        if req.contact_id in eve_characters:
            character = eve_characters[req.contact_id]
        else:
            # TODO: remove EveCharacterHelper usage
            character = EveCharacterHelper(req.contact_id)

        contact_name = character.character_name
        contact_icon_url = character.portrait_url(DEFAULT_ICON_SIZE)
        corporation_id = character.corporation_id
        corporation_name = (
            character.corporation_name if character.corporation_name else ""
        )
        corporation_ticker = (
            character.corporation_ticker if character.corporation_ticker else ""
        )
        alliance_id = character.alliance_id
        alliance_name = character.alliance_name if character.alliance_name else ""
        has_scopes = StandingRequest.has_required_scopes_for_request(
            character=character, user=req.user, quick_check=quick_check
        )

    elif req.is_corporation and req.contact_id in eve_corporations:
        corporation = eve_corporations[req.contact_id]
        contact_icon_url = corporation.logo_url(DEFAULT_ICON_SIZE)
        contact_name = corporation.corporation_name
        corporation_id = corporation.corporation_id
        corporation_name = corporation.corporation_name
        corporation_ticker = corporation.ticker
        alliance_id = None
        alliance_name = ""
        has_scopes = not corporation.is_npc and corporation.user_has_all_member_tokens(
            user=req.user, quick_check=quick_check
        )
    else:
        contact_name = ""
        contact_icon_url = ""
        corporation_id = None
        corporation_name = ""
        corporation_ticker = ""
        alliance_id = None
        alliance_name = ""
        has_scopes = False
    return (
        contact_name,
        contact_icon_url,
        corporation_id,
        corporation_name,
        corporation_ticker,
        alliance_id,
        alliance_name,
        has_scopes,
    )


def _fetch_labels(contacts, req):
    try:
        my_contact = contacts[req.contact_id]
    except KeyError:
        labels = []
    else:
        labels = my_contact.labels_sorted
    return labels
