import re
from importlib import import_module

from django.conf import settings


class WebFinger(object):

    def uri(self, name, *args):
        domain = settings.BASE_URL
        return "{domain}{name}".format(domain=domain, name=name)

    def response(self, response_dict, rel, acct):
        return response_dict


for package in settings.DJANGOLDP_PACKAGES:
    try:
        import_module('{}.endpoints.webfinger'.format(package))
    except ModuleNotFoundError:
        pass

model_classes = {cls.__name__: cls for cls in WebFinger.__subclasses__()}

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


class WebFingerEndpoint(object):
    """
    WebFinger endpoint
    See https://tools.ietf.org/html/rfc7033
    """

    def __init__(self, request):
        self.request = request
        self.params = {}
        self.acct = None

        self._extract_params()

    def _extract_params(self):
        # Because in this endpoint we handle both GET
        # and POST request.
        query_dict = (self.request.POST if self.request.method == 'POST'
                      else self.request.GET)

        self.params['resource'] = query_dict.get('resource', None)
        self.params['rel'] = query_dict.get('rel', None)

    def validate_params(self):
        """
        A resource must be set.
        """

        if self.params['resource'] is None:
            raise WebFingerError('invalid_request')

        try:
            self.acct = Acct(self.params['resource'])
        except ValueError:
            raise WebFingerError('invalid_acct_format')

    def response(self):
        """
        This endpoint only reply to rel="http://openid.net/specs/connect/1.0/issuer"
        :return: a dict representing the Json response
        """

        dict = {
            'subject': self.params['resource'],
            'aliases': [],
            'links': []
        }

        for class_name in model_classes:
            model_class = model_classes[class_name]
            webfinger = model_class()
            dict = webfinger.response(dict, self.params['rel'], self.acct)

        return dict


class WebFingerError(Exception):
    _errors = {
        'invalid_request': "The request provider parameter must contains an url or an email",
        'invalid_acct_format': "Invalid acct format"
    }

    def __init__(self, error=None, dict=None):
        if dict is None:
            self.error = error
            self.description = self._errors.get(error)
        else:
            self.error = dict['error']
            self.description = dict['error_description']

    def create_dict(self):
        dic = {
            'error': self.error,
            'error_description': self.description,
        }

        return dic
