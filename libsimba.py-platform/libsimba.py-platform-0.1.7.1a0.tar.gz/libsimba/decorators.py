from functools import wraps
from libsimba.auth.pkce import Pkce
from libsimba.auth.client_credentials import ClientCredentials
from libsimba.settings import AUTH_FLOW
from libsimba.settings import CLIENT_ID, CLIENT_SECRET, SCOPE, AUTH_FLOW, TENANT_ID
from libsimba.utils import SearchFilter

_ = {"pkce": Pkce, "client_credentials": ClientCredentials}

auth_flow = AUTH_FLOW.lower()


def auth_required_static(func):
    @wraps(func)
    def _auth_required_fn_wrapper(*args, **kwargs):
        try:
            check_creds()
        except Exception as e1:
            raise e1
        access_token = _[auth_flow].login()
        return func(
            {"Authorization": "Bearer {}".format(access_token)}, *args, **kwargs
        )

    return _auth_required_fn_wrapper


def auth_required(func):
    @wraps(func)
    def _auth_required_fn_wrapper(self, *args, **kwargs):
        try:
            check_creds()
        except Exception as e1:
            raise e1
        access_token = _[auth_flow].login()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {access_token}"
        return func(self, headers, *args, **kwargs)

    return _auth_required_fn_wrapper


def check_creds():
    if (
        CLIENT_ID is None
        or SCOPE is None
        or TENANT_ID is None
        or (AUTH_FLOW == "client_credentials" and CLIENT_SECRET is None)
    ):
        raise Exception(
            """
            Could not get Auth token
            Please ensure that all of the following environment variables are set:
  
            AZURE_AUTH_APP_CLIENT_SECRET
            AZURE_AUTH_APP_CLIENT_ID
            AZURE_APP_ID
            AZURE_TENANT
            """
        )


def filter_set(func):
    @wraps(func)
    def _filter_set_fn_wrapper(
        self, *args, search_filter: SearchFilter = None, page_size: int = 1000
    ):
        query_args = dict()
        query_args.update({"limit": page_size})
        if search_filter is not None:
            query_args.update(search_filter.query_args)
        return func(self, query_args, *args)

    return _filter_set_fn_wrapper
