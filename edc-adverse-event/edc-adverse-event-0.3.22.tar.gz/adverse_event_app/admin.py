from django.contrib import admin
from edc_model_admin import SimpleHistoryAdmin

from edc_adverse_event.modeladmin_mixins import (
    AeFollowupModelAdminMixin,
    AeInitialModelAdminMixin,
)

from .models import AeFollowup, AeInitial


@admin.register(AeInitial)
class AeInitialAdmin(AeInitialModelAdminMixin, SimpleHistoryAdmin):
    pass


@admin.register(AeFollowup)
class AeFollowupAdmin(AeFollowupModelAdminMixin, SimpleHistoryAdmin):
    pass
