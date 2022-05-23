# add new installed apps
INSTALLED_APPS = [
    'oidc_provider'
]

# add a middleware
MIDDLEWARE = [
    'djangoldp_account.auth.middleware.JWTUserMiddleware'
]

# override authentication backends at package level
AUTHENTICATION_BACKENDS = [
    'djangoldp_account.auth.backends.EmailOrUsernameAuthBackend',
    'guardian.backends.ObjectPermissionBackend',
    'djangoldp_account.auth.backends.ExternalUserBackend'
]

# override core authentication model
AUTH_USER_MODEL = 'djangoldp_account.LDPUser'

# define default value for package vars
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/redirect-default/'
OIDC_USERINFO = 'djangoldp_account.settings.userinfo'
OIDC_REGISTRATION_ENDPOINT_REQ_TOKEN = False
OIDC_REGISTRATION_ENDPOINT_ALLOW_HTTP_ORIGIN = True
OIDC_IDTOKEN_SUB_GENERATOR = 'djangoldp_account.settings.sub_generator'
OIDC_IDTOKEN_EXPIRE = 60 * 60 * 1600
EMAIL_ON_ACCOUNT_CREATION = False
ANONYMOUS_USER_NAME = None
USER_ANONYMOUS_PERMISSIONS = ['add', 'view']
USER_AUTHENTICATED_PERMISSIONS = ['view', 'add']
USER_OWNER_PERMISSIONS = ['view', 'add', 'change']
GROUP_ANONYMOUS_PERMISSIONS = ['view']
GROUP_AUTHENTICATED_PERMISSIONS = ['view', 'add', 'change']
GROUP_OWNER_PERMISSIONS = ['view', 'add', 'change']
ACCOUNT_ACTIVATION_DAYS = 7
