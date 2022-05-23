"""
This module contains the YAML configuration for a testing djangoldp server.
"""

yaml_config = """
dependencies:

ldppackages:
  - djangoldp.tests                         # fetch 'djangoldp.tests.djangoldp_settings'
  - djangoldp.tests.dummy.apps.DummyConfig  # already declared in 'djangoldp.tests'

server:
  ALLOWED_HOSTS:
    - '*'
  AUTH_USER_MODEL: tests.User
  EMAIL_HOST: somewhere
  ANONYMOUS_USER_NAME: None
  ROOT_URLCONF: djangoldp.urls
  SEND_BACKLINKS: false
  SITE_URL: http://happy-dev.fr
  BASE_URL: http://happy-dev.fr
  REST_FRAMEWORK:
    DEFAULT_PAGINATION_CLASS: djangoldp.pagination.LDPPagination
    PAGE_SIZE: 5
  USE_TZ: false
  SEND_BACKLINKS: false
  GUARDIAN_AUTO_PREFETCH: true
  SERIALIZER_CACHE: false
"""
