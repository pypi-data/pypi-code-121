from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from ..tasks import update_all


@login_required
@staff_member_required
def admin_changeset_update_now(request):
    update_all.delay(user_pk=request.user.pk)
    messages.info(
        request,
        _(
            "Started updating contacts and affiliations. "
            "You will receive a notification when completed."
        ),
    )
    return redirect("admin:standingsrequests_contactset_changelist")
