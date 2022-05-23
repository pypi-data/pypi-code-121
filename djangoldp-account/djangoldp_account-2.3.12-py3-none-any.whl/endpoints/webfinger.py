import re
from urllib.parse import urlparse

from django.contrib.auth import get_user_model

from djangoldp.endpoints.webfinger import WebFinger

ACCT_RE = re.compile(
    r'(?:acct:)?(?P<userinfo>[\w.!#$%&\'*+-/=?^_`{|}~]+)@(?P<host>[\w.:-]+)')


class Acct(object):
    def __init__(self, acct):
        m = ACCT_RE.match(acct)
        if not m:
            raise ValueError('invalid acct format')
        (userinfo, host) = m.groups()
        self.userinfo = userinfo
        self.host = host


class AccountWebFinger(WebFinger):

    def response(self, response_dict, rel, acct):
        '''responds to web finger request with user and OIDC issuer information'''
        if rel is None or "http://openid.net/specs/connect/1.0/issuer" in rel:
            user = get_user_model().objects.filter(username=acct.userinfo).first()
            if user is not None:
                url = urlparse(user.webid())
                if user.account.issuer is None:
                    href = "{}://{}".format(url.scheme, url.netloc)
                else:
                    href = user.account.issuer

                response_dict['links'].append({
                    'rel': "http://openid.net/specs/connect/1.0/issuer",
                    'href': href
                })

        return response_dict
