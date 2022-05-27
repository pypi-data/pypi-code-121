from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from eveuniverse.models import EveEntity

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from standingsrequests import __title__
from standingsrequests.app_settings import SR_PAGE_CACHE_SECONDS
from standingsrequests.core import BaseConfig
from standingsrequests.helpers.writers import UnicodeWriter
from standingsrequests.models import ContactSet, ContactType, StandingRequest

from ._common import DEFAULT_ICON_SIZE, add_common_context, label_with_icon

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("standingsrequests.request_standings")
def standings(request):
    try:
        contact_set = ContactSet.objects.latest()
    except ContactSet.DoesNotExist:
        contact_set = None
    finally:
        organization = BaseConfig.standings_source_entity()
        last_update = contact_set.date if contact_set else None
    context = {
        "lastUpdate": last_update,
        "organization": organization,
        "show_mains": request.user.has_perm("standingsrequests.view"),
    }
    return render(
        request,
        "standingsrequests/standings.html",
        add_common_context(request, context),
    )


@cache_page(SR_PAGE_CACHE_SECONDS)
@login_required
@permission_required("standingsrequests.request_standings")
def character_standings_data(request):
    try:
        contacts = ContactSet.objects.latest()
    except ContactSet.DoesNotExist:
        contacts = ContactSet()
    character_contacts_qs = (
        contacts.contacts.filter_characters()
        .select_related(
            "eve_entity",
            "eve_entity__character_affiliation",
            "eve_entity__character_affiliation__corporation",
            "eve_entity__character_affiliation__alliance",
            "eve_entity__character_affiliation__faction",
            "eve_entity__character_affiliation__eve_character",
            "eve_entity__character_affiliation__eve_character__character_ownership__user",
            "eve_entity__character_affiliation__eve_character__character_ownership__user__profile__main_character",
            "eve_entity__character_affiliation__eve_character__character_ownership__user__profile__state",
        )
        .prefetch_related("labels")
        .order_by("eve_entity__name")
    )
    characters_data = list()
    for contact in character_contacts_qs:
        character_name_html = label_with_icon(
            contact.eve_entity.icon_url(), contact.eve_entity.name
        )
        if request.user.has_perm("standingsrequests.view"):
            (
                state,
                main_character_name,
                main_character_html,
            ) = _identify_main_for_character(contact)
        else:
            state = main_character_name = main_character_html = ""
        corporation_name, alliance_name, faction_name = _identify_character_assoc(
            contact
        )
        labels = contact.labels_sorted
        characters_data.append(
            {
                "character_id": contact.eve_entity_id,
                "character_name_html": {
                    "display": character_name_html,
                    "sort": contact.eve_entity.name,
                },
                "corporation_name": corporation_name,
                "alliance_name": alliance_name,
                "faction_name": faction_name,
                "standing": contact.standing if contact.standing else "",
                "labels_str": ", ".join(labels),
                "main_character_name": main_character_name,
                "main_character_html": {
                    "display": main_character_html,
                    "sort": main_character_name,
                },
                "state": state,
            }
        )
    return JsonResponse({"data": characters_data})


def _identify_main_for_character(contact):
    try:
        character = contact.eve_entity.character_affiliation.eve_character
        user = character.character_ownership.user
    except (AttributeError, ObjectDoesNotExist):
        state = main_character_name = main_character_html = "-"
    else:
        main = user.profile.main_character
        state = user.profile.state.name if user.profile.state else "-"
        main_character_name = main.character_name
        main_character_ticker = main.corporation_ticker
        main_character_icon_url = main.portrait_url(DEFAULT_ICON_SIZE)
        main_character_html = label_with_icon(
            main_character_icon_url,
            f"[{main_character_ticker}] {main_character_name}",
        )

    return state, main_character_name, main_character_html


def _identify_character_assoc(contact):
    try:
        assoc = contact.eve_entity.character_affiliation
    except (AttributeError, ObjectDoesNotExist):
        corporation_name = "?"
        alliance_name = "?"
        faction_name = "?"
    else:
        corporation_name = assoc.corporation.name
        alliance_name = assoc.alliance.name if assoc.alliance else ""
        faction_name = assoc.faction.name if assoc.faction else ""
    return corporation_name, alliance_name, faction_name


@login_required
@permission_required("standingsrequests.download")
def download_pilot_standings(request):
    logger.info("download_pilot_standings called by %s", request.user)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="standings.csv"'
    writer = UnicodeWriter(response)
    try:
        contacts = ContactSet.objects.latest()
    except ContactSet.DoesNotExist:
        contacts = ContactSet()
    writer.writerow(
        [
            "character_id",
            "character_name",
            "corporation_id",
            "corporation_name",
            "corporation_ticker",
            "alliance_id",
            "alliance_name",
            "has_scopes",
            "state",
            "main_character_name",
            "main_character_ticker",
            "standing",
            "labels",
        ]
    )

    # lets request make sure all info is there in bulk
    character_contacts = contacts.contacts.all().order_by("eve_entity__name")
    EveEntity.objects.bulk_resolve_names([p.contact_id for p in character_contacts])

    for pilot_standing in character_contacts:
        try:
            char = EveCharacter.objects.get(character_id=pilot_standing.contact_id)
        except EveCharacter.DoesNotExist:
            char = None
        main = ""
        state = ""
        try:
            ownership = CharacterOwnership.objects.get(character=char)
        except CharacterOwnership.DoesNotExist:
            main_character_name = ""
            main = None
        else:
            state = ownership.user.profile.state.name
            main = ownership.user.profile.main_character
            if main is None:
                main_character_name = ""
            else:
                main_character_name = main.character_name
        pilot = [
            pilot_standing.eve_entity_id,
            pilot_standing.eve_entity.name,
            char.corporation_id if char else "",
            char.corporation_name if char else "",
            char.corporation_ticker if char else "",
            char.alliance_id if char else "",
            char.alliance_name if char else "",
            StandingRequest.has_required_scopes_for_request(char),
            state,
            main_character_name,
            main.corporation_ticker if main else "",
            pilot_standing.standing,
            ", ".join([label.name for label in pilot_standing.labels.all()]),
        ]
        writer.writerow([str(v) if v is not None else "" for v in pilot])
    return response


@cache_page(SR_PAGE_CACHE_SECONDS)
@login_required
@permission_required("standingsrequests.request_standings")
def corporation_standings_data(request):
    try:
        contacts = ContactSet.objects.latest()
    except ContactSet.DoesNotExist:
        contacts = ContactSet()
    corporations_qs = (
        contacts.contacts.filter_corporations()
        .select_related(
            "eve_entity",
            "eve_entity__corporation_details",
            "eve_entity__corporation_details__alliance",
            "eve_entity__corporation_details__faction",
        )
        .prefetch_related("labels")
        .order_by("eve_entity__name")
    )
    corporations_data = list()
    standings_requests = {
        obj.contact_id: obj
        for obj in (
            StandingRequest.objects.filter(
                contact_type_id=ContactType.corporation_id
            ).filter(
                contact_id__in=list(
                    corporations_qs.values_list("eve_entity_id", flat=True)
                )
            )
        )
    }
    for contact in corporations_qs:
        alliance_name, faction_name = _identify_corporation_organizations(contact)
        if request.user.has_perm("standingsrequests.view"):
            (
                main_character_name,
                main_character_html,
                state_name,
            ) = _identify_corporation_main(standings_requests, contact)
        else:
            main_character_name = main_character_html = state_name = ""
        labels_str = ", ".join(contact.labels_sorted)
        corporation_html = label_with_icon(
            contact.eve_entity.icon_url(DEFAULT_ICON_SIZE), contact.eve_entity.name
        )
        corporations_data.append(
            {
                "corporation_id": contact.eve_entity_id,
                "corporation_html": {
                    "display": corporation_html,
                    "sort": contact.eve_entity.name,
                },
                "alliance_name": alliance_name,
                "faction_name": faction_name,
                "standing": contact.standing,
                "labels_str": labels_str,
                "state": state_name,
                "main_character_name": main_character_name,
                "main_character_html": {
                    "display": main_character_html,
                    "sort": main_character_name,
                },
            }
        )
    return JsonResponse({"data": corporations_data})


def _identify_corporation_organizations(contact):
    try:
        corporation_details = contact.eve_entity.corporation_details
    except (ObjectDoesNotExist, AttributeError):
        alliance_name = "?"
        faction_name = "?"
    else:
        alliance = corporation_details.alliance
        if alliance:
            alliance_name = alliance.name
        else:
            alliance_name = ""
        faction = corporation_details.faction
        if faction:
            faction_name = faction.name
        else:
            faction_name = ""
    return alliance_name, faction_name


def _identify_corporation_main(standings_requests, contact):
    try:
        standing_request = standings_requests[contact.eve_entity_id]
        user = standing_request.user
        main = user.profile.main_character
    except (KeyError, AttributeError, ObjectDoesNotExist):
        main_character_name = state_name = main_character_html = "-"
    else:
        main_character_name = main.character_name if main else "-"
        main_character_ticker = main.corporation_ticker if main else ""
        main_character_icon_url = main.portrait_url(DEFAULT_ICON_SIZE) if main else "-"
        if main_character_name:
            main_character_html = label_with_icon(
                main_character_icon_url,
                f"[{main_character_ticker}] {main_character_name}",
            )
        else:
            main_character_html = ""
        state_name = user.profile.state.name
    return main_character_name, main_character_html, state_name


@cache_page(SR_PAGE_CACHE_SECONDS)
@login_required
@permission_required("standingsrequests.request_standings")
def alliance_standings_data(request):
    try:
        contacts = ContactSet.objects.latest()
    except ContactSet.DoesNotExist:
        contacts = ContactSet()
    alliances_data = list()
    for contact in (
        contacts.contacts.filter_alliances()
        .select_related("eve_entity")
        .prefetch_related("labels")
        .order_by("eve_entity__name")
    ):
        alliance_html = label_with_icon(
            contact.eve_entity.icon_url(DEFAULT_ICON_SIZE), contact.eve_entity.name
        )
        alliances_data.append(
            {
                "alliance_id": contact.eve_entity_id,
                "alliance_html": {
                    "display": alliance_html,
                    "sort": contact.eve_entity.name,
                },
                "standing": contact.standing,
                "labels_str": ", ".join(contact.labels_sorted),
            }
        )
    return JsonResponse({"data": alliances_data})
