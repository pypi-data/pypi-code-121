
def setup_settings(settings, is_prod, **kwargs):

    settings['INSTALLED_APPS'] += [
        app for app in [
            'djforms',
            'pagination'
        ] if app not in settings['INSTALLED_APPS']
    ]
