from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EveEntity

from allianceauth.notifications import notify
from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from standingsrequests import __title__
from standingsrequests.app_settings import SR_NOTIFICATIONS_ENABLED
from standingsrequests.constants import DATETIME_FORMAT_HTML
from standingsrequests.core import BaseConfig
from standingsrequests.models import (
    RequestLogEntry,
    StandingRequest,
    StandingRevocation,
)

from ._common import add_common_context, compose_standing_requests_data

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("standingsrequests.affect_standings")
def manage_standings(request):
    context = {
        "organization": BaseConfig.standings_source_entity(),
        "requests_count": StandingRequest.objects.pending_requests().count(),
        "revocations_count": StandingRevocation.objects.pending_requests().count(),
    }
    return render(
        request,
        "standingsrequests/manage_requests.html",
        add_common_context(request, context),
    )


@login_required
@permission_required("standingsrequests.affect_standings")
def manage_requests_list(request):
    requests_qs = StandingRequest.objects.pending_requests()
    requests_data = compose_standing_requests_data(requests_qs)
    context = {"DATETIME_FORMAT_HTML": DATETIME_FORMAT_HTML, "requests": requests_data}
    return render(
        request, "standingsrequests/partials/manage_requests_list.html", context
    )


@login_required
@permission_required("standingsrequests.affect_standings")
def manage_revocations_list(request):
    revocations_qs = StandingRevocation.objects.pending_requests()
    revocations_data = compose_standing_requests_data(revocations_qs)
    context = {
        "DATETIME_FORMAT_HTML": DATETIME_FORMAT_HTML,
        "revocations": revocations_data,
    }
    return render(
        request, "standingsrequests/partials/manage_revocations_list.html", context
    )


@login_required
@permission_required("standingsrequests.affect_standings")
def manage_requests_write(request, contact_id):
    contact_id = int(contact_id)
    logger.debug("manage_requests_write called by %s", request.user)
    if request.method == "PUT":
        actioned = 0
        for r in StandingRequest.objects.filter(contact_id=contact_id):
            r.mark_actioned(request.user)
            RequestLogEntry.objects.create_from_standing_request(
                r, RequestLogEntry.Action.CONFIRMED, request.user
            )
            actioned += 1
        if actioned > 0:
            return HttpResponse("")
        return HttpResponseNotFound()
    elif request.method == "DELETE":
        standing_request = get_object_or_404(StandingRequest, contact_id=contact_id)
        RequestLogEntry.objects.create_from_standing_request(
            standing_request, RequestLogEntry.Action.REJECTED, request.user
        )
        standing_request.delete()
        if SR_NOTIFICATIONS_ENABLED:
            entity_name = EveEntity.objects.resolve_name(contact_id)
            title = _("Standing request for %s rejected" % entity_name)
            message = _(
                "Your standing request for '%s' has been rejected by %s."
                % (entity_name, request.user)
            )
            notify(user=standing_request.user, title=title, message=message)
        return HttpResponse("")
    return HttpResponseNotFound()


@login_required
@permission_required("standingsrequests.affect_standings")
def manage_revocations_write(request, contact_id):
    contact_id = int(contact_id)
    logger.debug(
        "manage_revocations_write called by %s for contact_id %s",
        str(request.user),
        contact_id,
    )
    if request.method == "PUT":
        actioned = 0
        for r in StandingRevocation.objects.filter(
            contact_id=contact_id, action_date__isnull=True
        ):
            r.mark_actioned(request.user)
            RequestLogEntry.objects.create_from_standing_request(
                r, RequestLogEntry.Action.CONFIRMED, request.user
            )
            actioned += 1
        if actioned > 0:
            return HttpResponse("")
        return HttpResponseNotFound
    elif request.method == "DELETE":
        standing_revocations_qs = StandingRevocation.objects.filter(
            contact_id=contact_id
        )
        standing_revocation = standing_revocations_qs.first()
        RequestLogEntry.objects.create_from_standing_request(
            standing_revocation, RequestLogEntry.Action.REJECTED, request.user
        )
        standing_revocations_qs.delete()
        if SR_NOTIFICATIONS_ENABLED and standing_revocation.user:
            entity_name = EveEntity.objects.resolve_name(contact_id)
            title = _("Standing revocation for %s rejected" % entity_name)
            message = _(
                "Your standing revocation for '%s' "
                "has been rejected by %s." % (entity_name, request.user)
            )
            notify(user=standing_revocation.user, title=title, message=message)
        return HttpResponse("")
    return HttpResponseNotFound()
