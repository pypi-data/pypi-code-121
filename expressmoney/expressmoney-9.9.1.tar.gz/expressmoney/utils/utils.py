__all__ = ('get_secret', 'get_ip', 'get_http_referer', 'allowed_ip', 'timeit')

import time

from django.conf import settings
from google.cloud import secretmanager
from google.cloud import secretmanager_v1

secret_manager_client = secretmanager.SecretManagerServiceClient()
access_secret_version = secretmanager_v1.types.service.AccessSecretVersionRequest()


def get_secret(secret_key: str):
    name = f'projects/{"1086735462412" if settings.IS_PROD else "506185804933"}/secrets/{secret_key}/versions/1'
    access_secret_version.name = name
    return secret_manager_client.access_secret_version(request=access_secret_version).payload.data.decode("utf-8")


def get_ip(request):
    """Get client ip from header"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip


def get_http_referer(request):
    """Get client referer from header"""
    http_referer = request.META.get('HTTP_REFERER')
    http_host = request.META.get('HTTP_HOST')
    return http_referer if http_referer else http_host


def allowed_ip(request):
    """Check client ip by white list"""
    user_ip = get_ip(request)

    for allow_ip in settings.ALLOWED_IP:
        if user_ip == allow_ip or user_ip.startswith(allow_ip):
            return True
    return False


def timeit(method):
    def wrapper(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result

    return wrapper
