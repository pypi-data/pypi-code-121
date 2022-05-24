
from djassets.webp import is_webp_supported


def webp(request):

    is_supported = is_webp_supported(request)

    return {
        'IMG_FORMAT': 'WEBP' if is_supported else 'JPEG',
        'IS_WEBP_SUPPORTED': is_supported
    }
