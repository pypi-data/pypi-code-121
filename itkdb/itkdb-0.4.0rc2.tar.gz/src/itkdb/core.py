import logging
import requests
from requests.status_codes import codes
import cachecontrol.caches.file_cache
from cachecontrol.heuristics import ExpiresAfter
from .caching import CacheControlAdapter, CacheController

from jose import jwt
import time
import os
import pickle  # nosec

from .settings import settings
from . import exceptions
from .version import __version__

log = logging.getLogger(__name__)


class User(object):
    def __init__(
        self,
        accessCode1=settings.ITKDB_ACCESS_CODE1,
        accessCode2=settings.ITKDB_ACCESS_CODE2,
        audience="https://itkpd-test.unicorncollege.cz",
        prefix_url=settings.ITKDB_AUTH_URL,
        jwtOptions=None,
        save_auth=None,
    ):

        # session handling (for injection in tests)
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "itkdb/{}".format(__version__)})
        # store last call to authenticate
        self._response = None
        self._status_code = None
        # store jwks for validation/verification
        self._jwks = None
        # store information after authorization occurs
        self._access_token = None
        self._raw_id_token = None
        self._id_token = None
        # initialization configuration
        self._accessCode1 = accessCode1
        self._accessCode2 = accessCode2
        self._audience = audience
        self._prefix_url = prefix_url
        # update jwtOptions if provided
        self._jwtOptions = {"leeway": 2}  # **jwtOptions, python3 only
        self._jwtOptions.update(jwtOptions or {})
        # serialization/persistence
        self._save_auth = save_auth
        self._load()

    def _load(self):
        if self._save_auth and os.path.isfile(self._save_auth):
            try:
                saved_user = pickle.load(open(self._save_auth, "rb"))  # nosec
                if saved_user.is_expired():
                    log.warning(
                        "Saved user session is expired in {}. Creating a new one.".format(
                            self._save_auth
                        )
                    )
                    return False
                if saved_user.is_authenticated():
                    self.__dict__.update(saved_user.__dict__)
                    return True
            except pickle.UnpicklingError:
                log.warning(
                    "Unable to load user session from {}. Creating a new one.".format(
                        self._save_auth
                    )
                )
            except KeyError:  # python2 specific error
                log.warning(
                    "Unable to load user session from {}. Creating a new one.".format(
                        self._save_auth
                    )
                )
            return False

    def _dump(self):
        if self.is_authenticated() and not self.is_expired() and self._save_auth:
            try:
                pickle.dump(self, open(self._save_auth, "wb"), pickle.HIGHEST_PROTOCOL)
                return True
            except (pickle.PicklingError, AttributeError, TypeError):
                log.warning(
                    "Unable to save user session to {}.".format(self._save_auth)
                )
            return False

    def _load_jwks(self, force=False):
        if self._jwks is None or force:
            self._jwks = self._session.get(
                "https://uuidentity.plus4u.net/uu-oidc-maing02/bb977a99f4cc4c37a2afce3fd599d0a7/oidc/listKeys"
            ).json()

    def _parse_id_token(self):
        if self._raw_id_token:
            self._load_jwks()
            self._id_token = jwt.decode(
                self._raw_id_token,
                self._jwks,
                algorithms="RS256",
                audience=self._audience,
                options=self._jwtOptions,
            )

    def authenticate(self):
        # if not expired, do nothing
        if self.is_authenticated():
            if not self.is_expired():
                return True
            log.warning("User session is expired. Creating a new one.")

        # session-less request
        response = self._session.post(
            requests.compat.urljoin(self._prefix_url, "grantToken"),
            json={
                "grant_type": "password",
                "accessCode1": self._accessCode1,
                "accessCode2": self._accessCode2,
                "scope": settings.ITKDB_ACCESS_SCOPE,
            },
        )
        self._response = response
        self._status_code = response.status_code
        self._access_token = response.json().get("access_token")
        self._raw_id_token = response.json().get("id_token")
        self._id_token = None

        # handle parsing the id token
        self._parse_id_token()

        if not self.is_authenticated():
            raise exceptions.ResponseException(self._response)
        else:
            self._dump()

    @property
    def accessCode1(self):
        return self._accessCode1

    @property
    def accessCode2(self):
        return self._accessCode2

    @property
    def access_token(self):
        return self._access_token

    @property
    def id_token(self):
        return self._id_token if self._id_token else {}

    @property
    def name(self):
        return self.id_token.get("name", "")

    @property
    def expires_at(self):
        return self.id_token.get("exp", 0)

    @property
    def expires_in(self):
        expires_in = self.expires_at - time.time()
        return 0 if expires_in < 0 else int(expires_in)

    @property
    def identity(self):
        return self.id_token.get("uuidentity", "")

    @property
    def bearer(self):
        return self._raw_id_token if self._raw_id_token else ""

    def is_authenticated(self):
        return bool(
            self._status_code == codes["ok"]
            and self._access_token
            and self._raw_id_token
        )

    def is_expired(self):
        return not (self.expires_in > 0)

    def __repr__(self):
        return "{0:s}(name={1:s}, expires_in={2:d}s)".format(
            self.__class__.__name__, self.name, self.expires_in
        )


class Session(requests.Session):
    STATUS_EXCEPTIONS = {
        codes["bad_gateway"]: exceptions.ServerError,
        codes["bad_request"]: exceptions.BadRequest,
        codes["conflict"]: exceptions.Conflict,
        codes["found"]: exceptions.Redirect,
        codes["forbidden"]: exceptions.Forbidden,
        codes["gateway_timeout"]: exceptions.ServerError,
        codes["internal_server_error"]: exceptions.ServerError,
        codes["media_type"]: exceptions.SpecialError,
        codes["not_found"]: exceptions.NotFound,
        codes["request_entity_too_large"]: exceptions.TooLarge,
        codes["service_unavailable"]: exceptions.ServerError,
        codes["unauthorized"]: exceptions.Forbidden,
        codes["unavailable_for_legal_reasons"]: exceptions.UnavailableForLegalReasons,
    }
    SUCCESS_STATUSES = {codes["created"], codes["ok"]}

    def __init__(
        self,
        user=None,
        prefix_url=settings.ITKDB_SITE_URL,
        save_auth=None,
        cache=cachecontrol.caches.file_cache.FileCache(".webcache"),
        expires_after=None,
    ):
        """
        user (itkdb.core.User): A user object. Create one if not specified.
        prefix_url (str): The prefix url to use for all requests.
        save_auth (str): A file path to where to save authentication information.
        cache (str): A CacheControl.caches object for cache (default: cachecontrol.caches.file_cache.FileCache)
        expires_after (dict): The arguments are the same as the datetime.timedelta object. This will override or add the Expires header and override or set the Cache-Control header to public.
        """
        super(Session, self).__init__()
        self.headers.update({"User-Agent": "itkdb/{}".format(__version__)})
        self.user = user if user else User(save_auth=save_auth)
        self.auth = self._authorize
        self.prefix_url = prefix_url
        # store last call
        self._response = None

        cache_options = {}
        if cache:
            cache_options.update(dict(cache=cache))
        # handle expirations for cache
        if expires_after and isinstance(expires_after, dict):
            cache_options.update(dict(heuristic=ExpiresAfter(**expires_after)))
        if cache_options:
            # add caching
            super(Session, self).mount(
                self.prefix_url,
                CacheControlAdapter(controller_class=CacheController, **cache_options),
            )

    def _authorize(self, req):
        if req.url.startswith(settings.ITKDB_SITE_URL):
            self.user.authenticate()
            req.headers.update(
                {"Authorization": "Bearer {0:s}".format(self.user.bearer)}
            )
        return req

    def _normalize_url(self, url):
        return requests.compat.urljoin(self.prefix_url, url)

    def _check_response(self, response):
        if response.status_code in self.STATUS_EXCEPTIONS:
            raise self.STATUS_EXCEPTIONS[response.status_code](response)

        try:
            response.raise_for_status()
        except:
            raise exceptions.UnhandledResponse(response)

    def prepare_request(self, request):
        request.url = self._normalize_url(request.url)
        return super(Session, self).prepare_request(request)

    def send(self, request, **kwargs):
        response = super(Session, self).send(request, **kwargs)
        self._response = response
        log.debug(
            "Response: {} ({} bytes)".format(
                response.status_code, response.headers.get("content-length")
            )
        )
        self._check_response(response)
        return response

    def request(self, method, url, *args, **kwargs):
        url = self._normalize_url(url)
        return super(Session, self).request(method, url, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        if len(args) == 1:
            return self.send(self.prepare_request(*args), **kwargs)
        else:
            return self.request(*args, **kwargs)
