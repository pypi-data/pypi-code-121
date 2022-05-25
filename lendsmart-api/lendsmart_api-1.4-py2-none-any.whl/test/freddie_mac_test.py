from lendsmart_api import LendsmartClient
from lendsmart_api.jwt.access_token.service_account import ServiceAccount

api_endpoint = "https://devapi.lendsmart.ai/api/v1"
service_account_key = """
"""

data = {
    'access_token':'la0qT0lrnsTN3fCn3gOOQVCdKDPZ'
}
l = LendsmartClient(ServiceAccount(service_account_key),api_endpoint)
authenticated_freddiemac = l.freddiemac.authenticate_freddiemac()
freddiemac_lpa = l.freddiemac.run_lpa('1668766894756790272',data)
print(freddiemac_lpa)
freddiemac_poll = l.freddiemac.poll_request_id('1668766894756790272',data)
print(freddiemac_poll)
