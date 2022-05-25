import os
import polib
import gettext
import re
from itertools import chain
from functools import reduce

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import AppRegistryNotReady
from django.views.i18n import JavaScriptCatalog, get_formats
from django.utils.translation import get_language
from django.views.decorators.cache import cache_page
from django.utils import timezone
from django.views.decorators.http import last_modified

from jsmin import jsmin


__all__ = (
    'LanguageTranslation',
    'JavaScriptCatalogView',
)


class CacheMixin(object):
    MAX_AGE = getattr(settings, 'VUEJS_CACHE_MAX_AGE', 60 * 60 * 30)
    LAST_MODIFIED_DATE = timezone.now()

    def get_cache_timeout(self):
        return self.MAX_AGE

    def dispatch(self, *args, **kwargs):
        if getattr(settings, 'VUEJS_CACHE', True):
            return last_modified(
              lambda req, **kw: self.LAST_MODIFIED_DATE)(
                   cache_page(self.get_cache_timeout())(
                    super(CacheMixin, self).dispatch))(*args, **kwargs)
        else:
            return super(CacheMixin, self).dispatch(*args, **kwargs)


class LanguageTranslation:
    getters = {
        '.po': polib.pofile,
        '.mo': polib.mofile,
    }

    def __init__(self, language, domain='django', apps=None):
        self.language = language
        self.domain = domain
        self.apps = set(apps) if apps is not None else apps

    def get_installed_apps_translation_paths(self):
        """
        Get translation file paths from each installed app.
        """
        try:
            app_configs = reversed(list(django_apps.get_app_configs()))
        except AppRegistryNotReady:
            raise AppRegistryNotReady(
                "The translation infrastructure cannot be initialized before "
                "the apps registry is ready. Check that you don't make "
                "non-lazy gettext calls at import time."
            )

        app_configs = (
            x for x in app_configs
            if self.apps is None or x.name in self.apps
        )
        apps_paths = []

        for app_config in app_configs:
            localedir = os.path.join(app_config.path, 'locale')

            if os.path.exists(localedir):
                apps_paths += self.find_translations(localedir)

        return apps_paths

    def get_local_translation_paths(self):
        """
        Merges translations defined in LOCALE_PATHS.
        """
        return reduce(
            lambda acc, x: acc + x,
            (
                self.find_translations(localedir)
                for localedir in reversed(settings.LOCALE_PATHS)
                if os.path.exists(localedir)
            ),
            []
        )

    def get_translation_paths(self):
        return (
            self.get_local_translation_paths() +
            self.get_installed_apps_translation_paths()
        )

    def find_translations(self, localedir):
        return gettext.find(
            self.domain,
            localedir=localedir,
            languages=[self.language],
            all=True
        )

    def get_translation(self, file):
        filename, ext = os.path.splitext(file)
        getter = self.getters.get(ext, polib.pofile)
        po_file = re.sub(r'\.mo$', '.po', file)

        if os.path.isfile(po_file):
            return polib.pofile(po_file).translated_entries()

        return []

    def get_translations(self):
        return chain(*(
            (
                entry for entry in self.get_translation(file)
                if not entry.obsolete
            )
            for file in self.get_translation_paths()
        ))


def filter_translations(translation: LanguageTranslation, extensions):
    return (
        e for e in translation.get_translations()
        if any(
            reduce(
                lambda acc, i: acc or x[0].endswith(i),
                extensions, False
            )
            for x in e.occurrences
        )
    )


class JavaScriptCatalogView(CacheMixin, JavaScriptCatalog):
    domain = 'django'
    extensions = ['js', 'vue', 'ts']

    def get(self, request, *args, **kwargs):
        locale = get_language()
        domain = kwargs.get('domain', self.domain)

        # If packages are not provided, default to all installed packages, as
        # DjangoTranslation without localedirs harvests them all.
        packages = kwargs.get('packages', '')
        packages = packages.split('+') if packages else self.packages

        self.translation = filter_translations(
            LanguageTranslation(
                locale,
                domain=domain,
                apps=packages
            ),
            self.extensions
        )

        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            'catalog': self.get_catalog(),
            'formats': get_formats(),
        }

    def get_catalog(self):
        return {
            e.msgid: e.msgstr
            for e in self.translation
        }

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response.content = jsmin(response.content.decode()).encode()

        return response
