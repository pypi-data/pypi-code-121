from typing import Optional, cast, Dict

from google.oauth2 import service_account
from google.analytics.admin import AnalyticsAdminServiceClient
from google.api_core.exceptions import PermissionDenied, InvalidArgument

from arcane.ga4.exception import GoogleAnalyticsV4AccountException
from arcane.core import BadRequestError, BaseAccount
from arcane.credentials import get_user_decrypted_credentials
from arcane.datastore import Client as DatastoreClient

from .helpers import get_google_analytics_v4_account


class GaV4Client:
    def __init__(
        self,
        gcp_service_account: str,
        property_id: str,
        base_account: Optional[BaseAccount] = None,
        ga_v4_account: Optional[Dict] = None,
        datastore_client: Optional[DatastoreClient] = None,
        gcp_project: Optional[str] = None,
        secret_key_file: Optional[str] = None,
        firebase_api_key: Optional[str] = None,
        auth_enabled: bool = True,
        clients_service_url: Optional[str] = None,
        user_email: Optional[str] = None
    ):

        self.property_id = property_id
        scopes = ['https://www.googleapis.com/auth/analytics.readonly']
        if gcp_service_account and (ga_v4_account or base_account or user_email):
            if user_email:
                creator_email = user_email
            else:
                if ga_v4_account is None:
                    base_account = cast(BaseAccount, base_account)
                    ga_v4_account = get_google_analytics_v4_account(
                        base_account=base_account,
                        clients_service_url=clients_service_url,
                        firebase_api_key=firebase_api_key,
                        gcp_service_account=gcp_service_account,
                        auth_enabled=auth_enabled
                    )

                creator_email = ga_v4_account['creator_email']

            if creator_email is not None:
                if not secret_key_file:
                    raise BadRequestError('secret_key_file should not be None while using user access protocol')

                self.credentials = get_user_decrypted_credentials(
                    user_email=creator_email,
                    secret_key_file=secret_key_file,
                    gcp_credentials_path=gcp_service_account,
                    gcp_project=gcp_project,
                    datastore_client=datastore_client
                )
            else:
                self.credentials = service_account.Credentials.from_service_account_file(gcp_service_account, scopes=scopes)
        elif gcp_service_account:
            ## Used when posting an account using our credential (it is not yet in our database)
            self.credentials = service_account.Credentials.from_service_account_file(gcp_service_account, scopes=scopes)
        else:
            raise BadRequestError('one of the following arguments must be specified: gcp_service_account and (google_ads_account or base_account or user_email)')



    def get_property_name(self) -> str:
        client = AnalyticsAdminServiceClient(credentials=self.credentials)

        try:
            property_ = client.get_property(name=f"properties/{self.property_id}")
        except PermissionDenied:
            raise GoogleAnalyticsV4AccountException(f'We cannot access your property with the id: {self.property_id} from the Arcane account. Are you sure you granted access and gave the correct ID?')
        except InvalidArgument as err:
            raise GoogleAnalyticsV4AccountException(str(err))
        return str(property_.display_name)
