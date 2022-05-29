from django.conf import settings

SETTINGS = {
    'DEFAULT_REQUEST_TIMEOUT': 10,
    'REFORMAT_ALL_ERRORS': True,
}

SETTINGS.update(getattr(settings, 'DJANGO_ON_CHAIN', {}))

if SETTINGS.get('DEFAULT_TIMEOUT'):
    # For backward compatibility until all clients are upgraded
    SETTINGS['DEFAULT_REQUEST_TIMEOUT'] = SETTINGS['DEFAULT_TIMEOUT']
