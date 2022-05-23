from django.utils.translation import ugettext_lazy as _
from django.db import models

from drf_user_activity_tracker_mongodb.utils import database_log_enabled

if database_log_enabled():
    """
    Load models only if DRF_ACTIVITY_TRACKER_DATABASE is True
    """

    class ActivityLog(object):
        class Meta(object):
            app_label = 'drf_user_activity_tracker_mongodb'
            object_name = 'activity_log'
            model_name = module_name = 'activity_log'
            verbose_name = _('activity log')
            verbose_name_plural = _('activity logs')
            abstract = False
            swapped = False
            app_config = ""

        _meta = Meta()
        objects = models.Manager()
