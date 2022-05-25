from django.conf import settings

BLACKLIST_STATE_NAME = getattr(settings, 'BLACKLIST_STATE_NAME', "Blacklist")
