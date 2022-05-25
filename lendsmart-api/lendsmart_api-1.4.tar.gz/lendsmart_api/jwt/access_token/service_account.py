import time

from lendsmart_api.jwt.access_token import AccessToken

class ServiceAccount:
    """Service Account used to access lendsmart Resources"""

    CONST_SERVICE_ACCOUNT_NAME = 'lendsmart-lamda'
    CONST_ISSUER = """lendsmart_sh/serviceaccount"""
    CONST_SUBJECT = """lendsmart_sh/serviceaccount/service-account.name"""

    def __init__(self, service_account_key):
        """:type str: Secret key file to handshake with apiserver"""
        self.service_account_key = service_account_key

    def bearer_token(self):
        return AccessToken(self.CONST_SUBJECT,
         self.CONST_ISSUER,
         self.service_account_key,
         self.CONST_SERVICE_ACCOUNT_NAME,
         None,
         None).to_jwt()
