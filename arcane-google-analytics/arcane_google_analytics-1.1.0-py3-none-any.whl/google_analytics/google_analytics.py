from typing import Optional

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .exceptions import GA_EXCEPTIONS_TO_RETRY, GoogleAnalyticsAccountLostAccessException, GoogleAnalyticsServiceDownException

def get_exception_message(view_id: str, access_token: Optional[str] = None) -> str:
    if access_token:
        return F"We cannot access your view with the id: {view_id}. Are you sure you have access and entered correct ID?"
    else:
        return F"We cannot access your view with the id: {view_id} from the Arcane account. Are you sure you granted access and gave the correct ID?"


def get_view_name(
    view_id: str,
    adscale_key: Optional[str] = None,
    access_token: Optional[str] = None
) -> Optional[str]:
    """
        From an view id check if user has access to it and return the name of view

        adscale_key or access_token must be specified
    """
    # Create service to access the Google Analytics API

    scopes = ['https://www.googleapis.com/auth/analytics.readonly']
    if access_token:
        credentials = Credentials(access_token, scopes=scopes[0])
    elif adscale_key:
        credentials = service_account.Credentials.from_service_account_file(adscale_key, scopes=scopes)
    else:
        raise ValueError('one of the following arguments must be specified: adscale_key or access_token')

    service = build('analytics', 'v3', credentials=credentials, cache_discovery=False)
    if 'ga:' in view_id:
        view_id = view_id.replace('ga:', '')

    try:
        views = service.management().profiles().list(accountId='~all', webPropertyId='~all').execute()
    except HttpError as err:
        if err.resp.status >= 400 and err.resp.status < 500:
            raise GoogleAnalyticsAccountLostAccessException(get_exception_message(view_id, access_token))

        else:
            raise GoogleAnalyticsServiceDownException(f"The Google Analytics API does not respond. Thus, we cannot check if we can access your Google Analytics account with the id: {view_id}. Please try later" )

    if view_id not in [view.get('id') for view in views.get('items', [])]:
            raise GoogleAnalyticsAccountLostAccessException(get_exception_message(view_id, access_token))


    for view in views.get('items', []):
        if view.get('id') == view_id:
            return view.get('name', '')

