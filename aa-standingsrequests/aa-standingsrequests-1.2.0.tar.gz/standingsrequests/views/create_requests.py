from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from esi.decorators import token_required
from eveuniverse.models import EveEntity

from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from standingsrequests import __title__
from standingsrequests.app_settings import SR_CORPORATIONS_ENABLED
from standingsrequests.constants import CreateCharacterRequestError
from standingsrequests.core import BaseConfig, MainOrganizations
from standingsrequests.decorators import token_required_by_state
from standingsrequests.helpers.evecorporation import EveCorporation
from standingsrequests.models import ContactSet, StandingRequest, StandingRevocation
from standingsrequests.tasks import update_all, update_associations_api

from ._common import DEFAULT_ICON_SIZE, add_common_context

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required(StandingRequest.REQUEST_PERMISSION_NAME)
def index_view(request):
    """index page is used as dispatcher"""
    app_count = (
        StandingRequest.objects.pending_requests().count()
        + StandingRevocation.objects.pending_requests().count()
    )
    if app_count > 0 and request.user.has_perm("standingsrequests.affect_standings"):
        return redirect("standingsrequests:manage")
    else:
        return redirect("standingsrequests:create_requests")


@login_required
@permission_required(StandingRequest.REQUEST_PERMISSION_NAME)
def create_requests(request):
    organization = BaseConfig.standings_source_entity()
    try:
        main_char_id = request.user.profile.main_character.character_id
    except AttributeError:
        main_char_id = None
    context = {
        "corporations_enabled": SR_CORPORATIONS_ENABLED,
        "organization": organization,
        "organization_image_url": organization.icon_url(size=DEFAULT_ICON_SIZE),
        "authinfo": {"main_char_id": main_char_id},
    }
    return render(
        request,
        "standingsrequests/create_requests.html",
        add_common_context(request, context),
    )


@login_required
@permission_required(StandingRequest.REQUEST_PERMISSION_NAME)
def request_characters(request):
    logger.debug("Start request_characters request")
    try:
        contact_set = ContactSet.objects.latest()
    except ContactSet.DoesNotExist:
        return render(
            request, "standingsrequests/error.html", add_common_context(request, {})
        )

    eve_characters_qs = EveCharacter.objects.filter(
        character_ownership__user=request.user
    ).select_related("character_ownership__user")
    eve_characters = {obj.character_id: obj for obj in eve_characters_qs}
    characters_with_standing = {
        contact["eve_entity_id"]: contact["standing"]
        for contact in (
            contact_set.contacts.filter(
                eve_entity_id__in=list(eve_characters.keys())
            ).values("eve_entity_id", "standing")
        )
    }
    characters_standings_requests = {
        obj.contact_id: obj
        for obj in (
            StandingRequest.objects.select_related("user")
            .filter(contact_id__in=eve_characters.keys())
            .annotate_is_pending()
            .annotate_is_actioned()
        )
    }
    characters_standing_revocation = {
        obj.contact_id: obj
        for obj in (
            StandingRevocation.objects.filter(
                contact_id__in=eve_characters.keys()
            ).annotate_is_pending()
        )
    }
    characters_data = list()
    for character in eve_characters.values():
        character_id = character.character_id
        standing = characters_with_standing.get(character_id)
        has_pending_request = (
            character_id in characters_standings_requests
            and characters_standings_requests[character_id].is_pending_annotated
        )
        has_pending_revocation = (
            character_id in characters_standing_revocation
            and characters_standing_revocation[character_id].is_pending_annotated
        )
        has_actioned_request = (
            character_id in characters_standings_requests
            and characters_standings_requests[character_id].is_actioned_annotated
        )
        has_standing = (
            character_id in characters_standings_requests
            and characters_standings_requests[character_id].is_effective
            and characters_standings_requests[character_id].user == request.user
        )
        characters_data.append(
            {
                "character": character,
                "standing": standing,
                "pendingRequest": has_pending_request,
                "pendingRevocation": has_pending_revocation,
                "requestActioned": has_actioned_request,
                "inOrganisation": MainOrganizations.is_character_a_member(character),
                "hasRequiredScopes": StandingRequest.has_required_scopes_for_request(
                    character, user=request.user, quick_check=True
                ),
                "hasStanding": has_standing,
            }
        )

    context = {"characters": characters_data}
    return render(
        request,
        "standingsrequests/partials/request_characters.html",
        add_common_context(request, context),
    )


@login_required
@permission_required(StandingRequest.REQUEST_PERMISSION_NAME)
def request_corporations(request):
    logger.debug("Start request_characters request")
    try:
        contact_set = ContactSet.objects.latest()
    except ContactSet.DoesNotExist:
        return render(
            request, "standingsrequests/error.html", add_common_context(request, {})
        )

    eve_characters_qs = EveCharacter.objects.filter(
        character_ownership__user=request.user
    ).select_related("character_ownership__user")
    corporation_ids = set(
        eve_characters_qs.exclude(corporation_id__in=MainOrganizations.corporation_ids)
        .exclude(alliance_id__in=MainOrganizations.alliance_ids)
        .values_list("corporation_id", flat=True)
    )
    corporations_standing_requests = {
        obj.contact_id: obj
        for obj in (
            StandingRequest.objects.select_related("user")
            .filter(contact_id__in=corporation_ids)
            .annotate_is_pending()
            .annotate_is_actioned()
        )
    }
    corporations_revocation_requests = {
        obj.contact_id: obj
        for obj in (
            StandingRevocation.objects.filter(contact_id__in=corporation_ids)
            .annotate_is_pending()
            .annotate_is_actioned()
        )
    }
    corporation_contacts = {
        obj.eve_entity_id: obj
        for obj in (contact_set.contacts.filter(eve_entity_id__in=corporation_ids))
    }
    corporations_data = list()
    for corporation in EveCorporation.get_many_by_id(corporation_ids):
        if corporation and not corporation.is_npc:
            corporation_id = corporation.corporation_id
            try:
                standing = corporation_contacts[corporation_id].standing
            except KeyError:
                standing = None
            has_pending_request = (
                corporation_id in corporations_standing_requests
                and corporations_standing_requests[corporation_id].is_pending_annotated
            )
            has_pending_revocation = (
                corporation_id in corporations_revocation_requests
                and corporations_revocation_requests[
                    corporation_id
                ].is_pending_annotated
            )
            has_actioned_request = (
                corporation_id in corporations_standing_requests
                and corporations_standing_requests[corporation_id].is_actioned_annotated
            )
            has_standing = (
                corporation_id in corporations_standing_requests
                and corporations_standing_requests[corporation_id].is_effective
                and corporations_standing_requests[corporation_id].user == request.user
            )
            corporations_data.append(
                {
                    "token_count": corporation.member_tokens_count_for_user(
                        request.user, quick_check=True
                    ),
                    "corp": corporation,
                    "standing": standing,
                    "pendingRequest": has_pending_request,
                    "pendingRevocation": has_pending_revocation,
                    "requestActioned": has_actioned_request,
                    "hasStanding": has_standing,
                }
            )

    corporations_data.sort(key=lambda x: x["corp"].corporation_name)
    context = {"corps": corporations_data}
    return render(
        request,
        "standingsrequests/partials/request_corporations.html",
        add_common_context(request, context),
    )


@login_required
@permission_required(StandingRequest.REQUEST_PERMISSION_NAME)
def request_character_standing(request, character_id: int):
    """For a user to request standings for their own characters"""
    logger.debug(
        "Standings request from user %s for characterID %s",
        str(request.user),
        character_id,
    )
    character = get_object_or_404(
        EveCharacter.objects.select_related("character_ownership__user"),
        character_id=character_id,
    )
    error = StandingRequest.objects.create_character_request(request.user, character)
    if error is not CreateCharacterRequestError.NO_ERROR:
        if error is CreateCharacterRequestError.CHARACTER_IS_MISSING_SCOPES:
            messages.error(
                request,
                "You character %s is missing scopes."
                % EveEntity.objects.resolve_name(character_id),
            )
        elif error is CreateCharacterRequestError.USER_IS_NOT_OWNER:
            messages.error(
                request,
                "You are not the owner of character %s."
                % EveEntity.objects.resolve_name(character_id),
            )
        else:
            messages.error(
                request,
                "An unexpected error occurred when trying to process "
                "your standing request for %s. Please try again."
                % EveEntity.objects.resolve_name(character_id),
            )
    else:
        update_associations_api.delay()
    return redirect("standingsrequests:create_requests")


@login_required
@permission_required(StandingRequest.REQUEST_PERMISSION_NAME)
def remove_character_standing(request, character_id: int):
    """
    Handles both removing requests and removing existing standings
    """
    logger.debug(
        "remove_character_standing called by %s for character %s",
        str(request.user),
        character_id,
    )
    req = get_object_or_404(StandingRequest, user=request.user, contact_id=character_id)
    success = req.remove()
    if not success:
        messages.warning(
            request,
            "An unexpected error occurred when trying to process "
            "your request to revoke standing for %s. Please try again."
            % EveEntity.objects.resolve_name(character_id),
        )
    return redirect("standingsrequests:create_requests")


@login_required
@permission_required(StandingRequest.REQUEST_PERMISSION_NAME)
def request_corp_standing(request, corporation_id):
    """
    For a user to request standings for their own corp
    """
    corporation_id = int(corporation_id)
    logger.debug(
        "Standings request from user %s for corpID %d", request.user, corporation_id
    )
    if not StandingRequest.objects.create_corporation_request(
        request.user, corporation_id
    ):
        messages.warning(
            request,
            "An unexpected error occurred when trying to process "
            "your standing request for %s. Please try again."
            % EveEntity.objects.resolve_name(corporation_id),
        )
    else:
        update_associations_api.delay()
    return redirect("standingsrequests:create_requests")


@login_required
@permission_required(StandingRequest.REQUEST_PERMISSION_NAME)
def remove_corp_standing(request, corporation_id: int):
    """
    Handles both removing corp requests and removing existing standings
    """
    logger.debug("remove_corp_standing called by %s", request.user)
    try:
        req = StandingRequest.objects.filter(user=request.user).get(
            contact_id=corporation_id
        )
    except StandingRequest.DoesNotExist:
        success = False
    else:
        success = req.remove()
    if not success:
        messages.warning(
            request,
            "An unexpected error occurred when trying to process "
            "your request to revoke standing for %s. Please try again."
            % EveEntity.objects.resolve_name(corporation_id),
        )
    return redirect("standingsrequests:create_requests")


@login_required
@permission_required("standingsrequests.affect_standings")
@token_required(new=False, scopes=ContactSet.required_esi_scope())
def view_auth_page(request, token):
    source_entity = BaseConfig.standings_source_entity()
    char_name = EveEntity.objects.resolve_name(BaseConfig.owner_character_id)
    if not source_entity:
        messages.error(
            request,
            format_html(
                _(
                    "The configured character <strong>%s</strong> does not belong "
                    "to an alliance and can therefore not be used "
                    "to setup alliance standings. "
                    "Please configure a character that has an alliance."
                )
                % char_name,
            ),
        )
    elif token.character_id == BaseConfig.owner_character_id:
        update_all.delay(user_pk=request.user.pk)
        messages.success(
            request,
            format_html(
                _(
                    "Token for character <strong>%s</strong> has been setup "
                    "successfully and the app has started pulling standings "
                    "from <strong>%s</strong>."
                )
                % (char_name, source_entity.name),
            ),
        )
    else:
        messages.error(
            request,
            _(
                "Failed to setup token for configured character "
                "%(char_name)s (id:%(standings_api_char_id)s). "
                "Instead got token for different character: "
                "%(token_char_name)s (id:%(token_char_id)s)"
            )
            % {
                "char_name": char_name,
                "standings_api_char_id": BaseConfig.owner_character_id,
                "token_char_name": EveEntity.objects.resolve_name(token.character_id),
                "token_char_id": token.character_id,
            },
        )
    return redirect("standingsrequests:index")


@login_required
@permission_required(StandingRequest.REQUEST_PERMISSION_NAME)
@token_required_by_state(new=False)
def view_requester_add_scopes(request, token):
    messages.success(
        request,
        _("Successfully added token with required scopes for %(char_name)s")
        % {"char_name": EveEntity.objects.resolve_name(token.character_id)},
    )
    return redirect("standingsrequests:create_requests")
