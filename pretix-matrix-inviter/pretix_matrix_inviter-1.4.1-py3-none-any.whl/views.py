from django.urls import reverse
from pretix.base.models import Event
from pretix.control.views.event import EventSettingsFormView, EventSettingsViewMixin

from .forms import MatrixInviterForm


class MatrixInviterView(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    permission = "can_change_settings"
    form_class = MatrixInviterForm
    template_name = "pretix_matrix_inviter/settings.html"

    def get_success_url(self, **kwargs):
        return reverse(
            "plugins:pretix_matrix_inviter:settings",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
            },
        )
