import time

from lendsmart_api.jwt import Jwt

class AccessToken(Jwt):
    """Access Token used to access lendsmart Resources"""
    def __init__(self, account_sid, signing_key_sid, secret, service_account_name,
                 grants=None, identity=None, ttl=3600, valid_until=None):
        grants = grants or []

        self.account_sid = account_sid
        self.signing_key_sid = signing_key_sid
        self.identity = identity
        self.grants = grants
        self.secret = secret
        super(AccessToken, self).__init__(
            secret_key=self.secret,
            algorithm='RS256',
            issuer=signing_key_sid,
            subject=self.account_sid,
            service_account_name=service_account_name,
            ttl=ttl,
            valid_until=valid_until,
        )

    def _generate_headers(self):
        return {}

    def _generate_payload(self):
        now = int(time.time())
        payload = {
            'grants': {grant.key: grant.to_payload() for grant in self.grants}
        }
        if self.identity:
            payload['grants']['identity'] = self.identity
        return payload

    def __str__(self):
        return '<AccessToken {}>'.format(self.to_jwt())
