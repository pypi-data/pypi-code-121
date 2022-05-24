
import os

from django.apps import AppConfig
from django.conf import global_settings

from djassets.constants import STATIC_APPS_MAP


def setup_settings(settings, is_prod, **kwargs):

    base_dir = settings['BASE_DIR']

    extra_static_files = _get_extra_static_files(
        settings.get('STATIC_APPS', []))

    css_components = {
        'generic': {
            'source_filenames': (
                extra_static_files['css'] +
                settings.get('STYLESHEETS', [])
            ),
            'output_filename': 'cache/generic.css',
        }
    }

    if 'CSS_COMPONENTS' in settings:
        for key, filenames in settings['CSS_COMPONENTS'].items():
            css_components[key] = {
                'source_filenames': filenames,
                'output_filename': 'cache/{}.css'.format(key),
            }

    js_components = {
        'generic': {
            'source_filenames': (
                extra_static_files['js'] +
                settings.get('JAVASCRIPT', [])
            ),
            'output_filename': 'cache/generic.js',
        }
    }

    if 'JS_COMPONENTS' in settings:
        for key, filenames in settings['JS_COMPONENTS'].items():
            js_components[key] = {
                'source_filenames': filenames,
                'output_filename': 'cache/{}.js'.format(key),
            }

    settings.update({
        'STATICFILES_STORAGE': 'pipeline.storage.PipelineManifestStorage',
        'BOWER_INSTALLED_APPS': (
            extra_static_files['bower'] +
            settings.get('BOWER_INSTALLED_APPS', [])
        ),
        'BOWER_COMPONENTS_ROOT': os.path.join(base_dir, 'static'),
        'STATICFILES_DIRS': [
            os.path.join(base_dir, 'static'),
            os.path.join(base_dir, 'static', 'bower_components')
        ],
        'STATICFILES_FINDERS': global_settings.STATICFILES_FINDERS + [
            'pipeline.finders.PipelineFinder',
            'djangobower.finders.BowerFinder'
        ],
        'STATIC_URL': '/static/',
        'MEDIA_URL': '/media/',
        'PIPELINE': {
            'JS_COMPRESSOR': 'pipeline.compressors.jsmin.JSMinCompressor',
            'CSS_COMPRESSOR': 'pipeline.compressors.cssmin.CSSMinCompressor',
            'STYLESHEETS': css_components,
            'JAVASCRIPT': js_components
        },
        'THUMBNAIL_QUALITY': 85,
        'FILE_UPLOAD_PERMISSIONS': 0o755
    })

    settings['MIDDLEWARE'] += [
        'pipeline.middleware.MinifyHTMLMiddleware'
    ]

    for template in settings['TEMPLATES']:
        template['OPTIONS']['context_processors'].append(
            'djassets.context_processors.webp')

    extra_apps = [
        'djassets',
        'django.contrib.staticfiles',
        'pipeline',
        'djangobower',
        'django_cleanup',
        'sorl.thumbnail'
    ]

    installed_apps = settings['INSTALLED_APPS']

    for app in extra_apps:
        if app not in installed_apps:
            installed_apps.append(app)

    if is_prod:
        domain = settings.get('DOMAIN')

        if not domain:
            raise ValueError('Please add `DOMAIN` to settings')

        public_dir = os.path.join('/home/dev', 'sites', domain, 'public')

        settings['STATIC_ROOT'] = os.path.join(public_dir, 'static')
        settings['MEDIA_ROOT'] = os.path.join(public_dir, 'media')
    else:
        settings['STATIC_ROOT'] = os.path.join(base_dir, 'static-collect')
        settings['MEDIA_ROOT'] = os.path.join(base_dir, 'media')



def _get_extra_static_files(static_apps):

    components = {
        'bower': [],
        'css': [],
        'js': []
    }

    for app in static_apps:

        app_map = STATIC_APPS_MAP.get(app, {})

        for component in ['bower', 'css', 'js']:
            value = app_map.get(component)

            if value:
                if isinstance(value, str):
                    value = [value]

                components[component] += value

    return components


def _get_static_app_component_list(apps, files_map):

    result = []

    for app in apps:
        try:
            files = files_map[app]
        except KeyError:
            continue

        if isinstance(files, str):
            result.append(files)
        else:
            result += files

    return tuple(result)


class AssetsAppConfig(AppConfig):

    name = 'djassets'


default_app_config = 'djassets.AssetsAppConfig'
