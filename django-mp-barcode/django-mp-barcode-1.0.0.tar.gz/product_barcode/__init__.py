
def setup_settings(settings, **kwargs):

    if 'solo' not in settings['INSTALLED_APPS']:
        settings['INSTALLED_APPS'] += ['solo']
