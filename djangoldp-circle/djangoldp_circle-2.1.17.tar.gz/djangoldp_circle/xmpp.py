from django.conf import settings


XMPP_SERVERS = set({'51.15.243.248', '212.47.234.179', '2001:bc8:47b0:2711::1'})

if hasattr(settings, 'XMPP_SERVER_IP'):
    XMPP_SERVERS = XMPP_SERVERS.union(getattr(settings, 'XMPP_SERVER_IP'))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
