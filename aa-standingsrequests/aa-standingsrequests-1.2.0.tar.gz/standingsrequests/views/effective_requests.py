from django.contrib.auth.decorators import login_required, permission_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.views.decorators.cache import cache_page

from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from standingsrequests import __title__
from standingsrequests.app_settings import SR_PAGE_CACHE_SECONDS
from standingsrequests.constants import DATETIME_FORMAT_PY
from standingsrequests.core import BaseConfig
from standingsrequests.models import StandingRequest

from ._common import add_common_context, compose_standing_requests_data

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("standingsrequests.affect_standings")
def effective_requests(request):
    context = {
        "organization": BaseConfig.standings_source_entity(),
        "requests_count": _standing_requests_to_view().count(),
    }
    return render(
        request,
        "standingsrequests/effective_requests.html",
        add_common_context(request, context),
    )


@cache_page(SR_PAGE_CACHE_SECONDS)
@login_required
@permission_required("standingsrequests.affect_standings")
def effective_requests_data(request):
    requests_data = compose_standing_requests_data(
        _standing_requests_to_view(), quick_check=True
    )
    for req in requests_data:
        req["request_date_str"] = {
            "display": req["request_date"].strftime(DATETIME_FORMAT_PY),
            "sort": req["request_date"].isoformat(),
        }
        req["labels_str"] = ", ".join(req["labels"])
        scopes_html = (
            '<i class="fas fa-check fa-fw text-success" title="Has required scopes"></i>'
            if req["has_scopes"]
            else '<i class="fas fa-times fa-fw text-danger" title="Does not have required scopes"></i>'
        )
        req["scopes_state_html"] = format_html(
            "{} {}", format_html(scopes_html), req["state"]
        )
        effective_html = (
            '<i class="fas fa-check fa-fw text-success" title="Standing Effective"></i>'
            if req["is_effective"]
            else '<i class="fas fa-times fa-fw text-danger" title="Standing not effective"></i>'
        )
        req["effective_html"] = format_html(
            "{} {}", format_html(effective_html), req["action_by"]
        )
        # remove columns that are not needed to reduce data volume
        del req["request_date"]
        del req["reason"]
        del req["main_character_ticker"]
        del req["main_character_icon_url"]
        del req["contact_icon_url"]
        del req["corporation_id"]
        del req["alliance_id"]
        del req["labels"]
        del req["is_effective"]
        del req["is_character"]
        del req["is_corporation"]
        del req["actioned"]
    return JsonResponse({"data": requests_data})


def _standing_requests_to_view() -> models.QuerySet:
    return (
        StandingRequest.objects.filter(is_effective=True)
        .select_related("user__profile")
        .order_by("-request_date")
    )
