# ############################################################
#
#   Copy this file to local_settings.py and update the values
#   as needed for the local runtime environment.
#
# ############################################################

# Environment choices: {DEV, TEST, PROD}
ENVIRONMENT = 'DEV'

# Name of machine running the application
ALLOWED_HOSTS = ['localhost']

# Debug mode (probably only true in DEV)
DEBUG = True

# SSO URL
CAS_SERVER_URL = 'https://sso-stage.oit.pdx.edu/idp/profile/cas/login'

# Finti URL (dev, test, or prod)
FINTI_URL = 'https://ws.oit.pdx.edu'
# Finti URLs (for reference)
# http://localhost:8888
# https://sf-stage.oit.pdx.edu
# https://ws.oit.pdx.edu

FINTI_TOKEN = "2144402c-586e-44fc-bd0c-62b31e98394d"

# As-of psu-base 0.11.0, Finti responses can be cached for offline development
# Override these in local_settings.py
FINTI_SIMULATE_WHEN_POSSIBLE = True    # Simulate Finti calls (i.e. when not on VPN)
FINTI_SAVE_RESPONSES = True    # Save/record actual Finti responses for offline use?
