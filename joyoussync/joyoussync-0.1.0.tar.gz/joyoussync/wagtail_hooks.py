from django.utils.translation import gettext_lazy as _
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import SyncJob


@modeladmin_register
class SyncJobAdmin(ModelAdmin):
    model = SyncJob
    menu_label = _('Calendar Sync Jobs')
    menu_icon = 'date'
    add_to_settings_menu = True
    list_display = ('link',)
    search_fields = ('link',)
