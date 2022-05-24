import otree
from django.conf import settings
from django.http import HttpResponseRedirect
from otree.views.participant import (
    vanilla,
    get_object_or_404,
    participant_or_none_if_exceeded,
    no_participants_left_http_response,
)


class JoinSessionAnonymouslyWithParams(vanilla.View):
    """
    Copied from otree.views.participant.JoinSessionAnonymously
    (since participant is not saved by JoinSessionAnonymously)
    """

    url_pattern = r"^join/(?P<anonymous_code>[a-z0-9]+)/$"

    def get(self, request, anonymous_code):
        session = get_object_or_404(
            otree.models.Session, _anonymous_code=anonymous_code
        )
        label = self.request.GET.get("participant_label")
        participant = participant_or_none_if_exceeded(session, label=label)
        if not participant:
            return no_participants_left_http_response()
        # custom: preserve GET parameters
        participant.vars["init_get_params"] = self.request.GET.dict()
        participant.vars["lang"] = participant.vars["init_get_params"].get(
            "QSL", settings.LANGUAGE_CODE
        )
        participant.save()
        # end custom
        return HttpResponseRedirect(participant._start_url())
