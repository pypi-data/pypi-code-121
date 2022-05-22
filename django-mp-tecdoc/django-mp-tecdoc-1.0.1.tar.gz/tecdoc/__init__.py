
def setup_settings(settings, is_prod, **kwargs):

    if 'TECDOC_HOST' in settings:
        settings['DATABASES'] = {
            'tecdoc': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'tecdoc',
                'USER': 'tecdoc',
                'HOST': settings['TECDOC_HOST'],
                'PASSWORD': settings['TECDOC_PASSWORD']
            },
            **settings.get('DATABASES', {})
        }

    settings['DATABASE_ROUTERS'] = settings.get('DATABASE_ROUTERS', []) + [
        'tecdoc.routers.TecDocRouter'
    ]
