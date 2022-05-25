
from typing import Dict, List, Optional, cast
import backoff
import json
import logging

from arcane.core.exceptions import BadRequestError
from arcane.core.types import BaseAccount
from arcane.datastore import Client as DatastoreClient

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from arcane.credentials import get_user_decrypted_credentials

from .exceptions import GoogleAnalyticsAccountLostAccessException, GoogleAnalyticsServiceDownException, GA_EXCEPTIONS_TO_RETRY
from .helpers import get_google_analytics_account

class GaClient:
    def __init__(
        self,
        gcp_credentials_path: str,
        ga_view_id: str,
        base_account: Optional[BaseAccount] = None,
        account_ga: Optional[Dict] = None,
        datastore_client: Optional[DatastoreClient] = None,
        gcp_project: Optional[str] = None,
        secret_key_file: Optional[str] = None,
        firebase_api_key: Optional[str] = None,
        auth_enabled: bool = True,
        clients_service_url: Optional[str] = None,
        user_email: Optional[str] = None
    ):
        self.ga_view_id = ga_view_id.replace('ga:', '')

        scopes = ['https://www.googleapis.com/auth/analytics.readonly']
        if gcp_credentials_path and (account_ga or base_account or user_email):

            if user_email:
                creator_email = user_email
            else:
                if account_ga is None:
                    base_account = cast(BaseAccount, base_account)
                    account_ga = get_google_analytics_account(
                        base_account=base_account,
                        clients_service_url=clients_service_url,
                        firebase_api_key=firebase_api_key,
                        gcp_credentials_path=gcp_credentials_path,
                        auth_enabled=auth_enabled
                    )

                creator_email = account_ga['creator_email']

            if creator_email is not None:
                if not secret_key_file:
                    raise BadRequestError('secret_key_file should not be None while using user access protocol')

                self.credentials = get_user_decrypted_credentials(
                    user_email=creator_email,
                    secret_key_file=secret_key_file,
                    gcp_credentials_path=gcp_credentials_path,
                    gcp_project=gcp_project,
                    datastore_client=datastore_client
                )
            else:
                self.credentials = service_account.Credentials.from_service_account_file(gcp_credentials_path, scopes=scopes)
        elif gcp_credentials_path:
            ## Used when posting an account using our credential (it is not yet in our database)
            self.credentials = service_account.Credentials.from_service_account_file(gcp_credentials_path, scopes=scopes)
        else:
            raise BadRequestError('one of the following arguments must be specified: gcp_service_account and (google_ads_account or base_account or user_email)')

    def init_service(self, scope):
        version = 'v3' if scope == 'analytics' else 'v4'
        service = build(scope, version, credentials=self.credentials, cache_discovery=False)
        return service

    def __get_exception_message__(self) -> str:
        return f'We cannot access your view with the id: {self.ga_view_id} from the Arcane account. Are you sure you granted access and gave the correct ID?'

    def check_access(self):
        self.get_view_name()

    @backoff.on_exception(backoff.expo, (GA_EXCEPTIONS_TO_RETRY), max_tries=3)
    def get_metrics_from_view(self,
                            date_ranges: Optional[List[Dict]]=None,
                            metrics: Optional[List]=None,
                            **optional_params):
        """
        helper to call the Google Analytics Core Reporting API. More information on the following link :
        https://developers.google.com/analytics/devguides/reporting/core/v4/basics
        """

        if metrics is None:
            metrics = [{'expression': 'ga:transactions'}]
        if date_ranges is None:
            date_ranges = [{'startDate': '30daysAgo', 'endDate': 'yesterday'}]

        required_params = {
            'viewId': self.ga_view_id,
            'dateRanges': date_ranges,
            'metrics': metrics
            }
        body = {'reportRequests': [{ **required_params, **optional_params}]}

        service = self.init_service('analyticsreporting')
        try:
            res = service.reports().batchGet(body=body).execute()
        except HttpError as err:
            message = json.loads(err.content).get('error').get('message')
            raise BadRequestError(f'Error while getting data from GA. "{message}"') from err
        logging.info(res)
        return res

    @backoff.on_exception(backoff.expo, (GA_EXCEPTIONS_TO_RETRY), max_tries=3)
    def get_view_name(self) -> Optional[str]:
        """
            From an view id check if user has access to it and return the name of view

            gcp_credentials_path or access_token must be specified
        """
        # Create service to access the Google Analytics API


        service = self.init_service('analytics')
        try:
            views = service.management().profiles().list(accountId='~all', webPropertyId='~all').execute()
        except HttpError as err:
            if err.resp.status >= 400 and err.resp.status < 500:
                raise GoogleAnalyticsAccountLostAccessException(self.__get_exception_message__())
            else:
                raise GoogleAnalyticsServiceDownException(f"The Google Analytics API does not respond. Thus, we cannot check if we can access your Google Analytics account with the id: {self.ga_view_id}. Please try later" )

        if self.ga_view_id not in [view.get('id') for view in views.get('items', [])]:
            raise GoogleAnalyticsAccountLostAccessException(self.__get_exception_message__())

        for view in views.get('items', []):
            if view.get('id') == self.ga_view_id:
                return view.get('name', '')
