from directory_client_core.authentication import SessionSSOAuthenticator

from directory_api_client.base import AbstractAPIClient

url_enrolment = '/enrolment/'
url_preverified = '/enrolment/preverified-company/{key}/'
url_preverified_claim = '/enrolment/preverified-company/{key}/claim/'


class EnrolmentAPIClient(AbstractAPIClient):
    def send_form(self, form_data):
        return self.post(url=url_enrolment, data=form_data)

    def retrieve_prepeveried_company(self, key):
        return self.get(url=url_preverified.format(key=key), use_fallback_cache=True)

    def claim_prepeveried_company(self, sso_session_id, key, data):
        return self.post(
            url=url_preverified_claim.format(key=key),
            data=data,
            authenticator=SessionSSOAuthenticator(sso_session_id),
        )
