
import httpagentparser


WEBP_VALID_BROWSERS = ['Chrome', 'Opera', 'Opera Mobile']


def is_webp_supported(request):

    user_agent = request.META.get('HTTP_USER_AGENT')
    http_accept = request.META.get('HTTP_ACCEPT', '')

    if 'webp' in http_accept:
        return True

    if user_agent:
        data = httpagentparser.detect(user_agent)
        if 'browser' in data:
            return data['browser']['name'] in WEBP_VALID_BROWSERS

    return False
