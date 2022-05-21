import json
import os
from os.path import join, dirname

DEBUG = True

PROJECT_PATH = dirname(__file__)

# Default settings
BASE_API_URL = "https://api.sep.dev.simbachain.com"
AUTH_FLOW = "client_credentials"
CLIENT_SECRET = ""
CLIENT_ID = ""
SCOPE = "api://{}/scaas.access".format(CLIENT_ID)
BASE_AUTH_URL = "https://login.microsoftonline.com"
TENANT_ID = ""
AUTH_ENDPOINT = "/{}/oauth2/v2.0/".format(TENANT_ID)

# Use the env to override local_settings
# So load local_settings first
try:
    from libsimba.local_settings import *
except ModuleNotFoundError as e1:
    # Ignore if the local_settings file is missing
    pass

# SCAAS API & Auth settings
# Load from local_setting, then override with env var if present
BASE_API_URL = os.getenv("LIBSIMBA_BASE_API_URL", BASE_API_URL)

# Options: client_credentials (Default), pkce, password
AUTH_FLOW = os.getenv("LIBSIMBA_AUTH_FLOW", AUTH_FLOW)

# [Optional] CLIENT_SECRET is only needed if using the client credentials flow.
CLIENT_SECRET = os.getenv("LIBSIMBA_AUTH_APP_CLIENT_SECRET", CLIENT_SECRET)

CLIENT_ID = os.getenv("LIBSIMBA_AUTH_APP_CLIENT_ID", CLIENT_ID)

SCOPE = os.getenv("LIBSIMBA_AUTH_APP_SCOPE", SCOPE)

BASE_AUTH_URL = os.getenv("LIBSIMBA_AUTH_BASE_URL", BASE_AUTH_URL)

TENANT_ID = REALM_ID = os.getenv("LIBSIMBA_AUTH_TENANT_ID", TENANT_ID)

AUTH_ENDPOINT = os.getenv("LIBSIMBA_AUTH_ENDPOINT", AUTH_ENDPOINT)

# Test settings
TEST_APP = "<set in local settings>"
TEST_CONTRACT = "<set in local settings>"
TEST_METHOD = "<set in local settings>"
TEST_INPUTS = []
TEST_APP = os.getenv("LIBSIMBA_APP", TEST_APP)
TEST_CONTRACT = os.getenv("LIBSIMBA_CONTRACT", TEST_CONTRACT)
TEST_METHOD = os.getenv("LIBSIMBA_METHOD", TEST_METHOD)
test_input_json = os.getenv("LIBSIMBA_INPUTS", None)
if test_input_json:
    TEST_INPUTS = json.loads(test_input_json)
