from servicefoundry.internal import lib


def login(api_key=None):
    lib.login(api_key=api_key, interactive=False if api_key else True)
