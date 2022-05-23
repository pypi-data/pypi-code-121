
from os.path import splitext, join

from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag(takes_context=True)
def static_img(context, path):

    is_webp_supported = context.get('IS_WEBP_SUPPORTED')

    folder = 'webp' if is_webp_supported else 'img'

    if is_webp_supported:
        path = splitext(path)[0] + '.webp'

    return join(settings.STATIC_URL, folder, path)
