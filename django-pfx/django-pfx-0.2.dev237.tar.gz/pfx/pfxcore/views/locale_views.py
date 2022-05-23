from django.conf import settings
from django.core.cache import cache
from django.utils import translation

from babel import Locale

from pfx.pfxcore.decorator import rest_api, rest_view
from pfx.pfxcore.http import JsonResponse

from .rest_views import BaseRestView


def get_locales():
    return [
        dict(
            pk=code,
            name=Locale.parse(translation.to_locale(code)).get_display_name())
        for code, __ in settings.LANGUAGES]


def get_languages_json():
    locales = get_locales()
    return {
        'items': locales, 'meta': {'count': len(locales)}}


@rest_view("/locales")
class LocaleRestView(BaseRestView):
    @rest_api('/languages', public=True)
    def locales(self):
        data = cache.get_or_set('pfx.languages', get_languages_json, 60 * 60)
        return JsonResponse(data)
