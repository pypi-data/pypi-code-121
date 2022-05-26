import requests, json, time
from .rest import RestURL

def craft_error_message(resp, url):
    code = resp.status_code

    if code in [404]:
        raise Exception("Server Error: " + str(code), resp.text, " URL: ", str(url))

    if code in [503, 500]:
        raise Exception("Server Error: " + str(code), " URL: ", str(url))

    if code == 401:
        raise Exception("Server returned 401: Unauthorized. Please check username or password.")

    json_data = resp.json()
    error_message = json_data["error"] + "--" + json_data["error_description"]
    raise Exception("Error: " + str(code) + " \n for URL:" + str(url) + " \n Response: " + error_message)


# Retrieves the Well Known Endpoint: https://openid.net/specs/openid-connect-discovery-1_0.html
def get_well_known_info(url, realm):
    discovery_url = RestURL(url, ['auth', 'realms', realm, '.well-known', 'openid-configuration'])

    resp = requests.get(url=str(discovery_url))

    if resp.status_code == 200:
        return resp.json()

    craft_error_message(resp, url)


def elapsed_time(time2):
    return (time.time() - time2)

class Token:
    def __init__(self, well_known={}, payload=None, refresh_token=None, raw_json_str=None, client_id=None):
        self.token = None
        self.refresh_token = None
        self.expiring = 60
        self.well_known = well_known
        self.start_time = 0
        self.payload = None
        self.client_id = client_id if client_id else "admin-cli"


        if payload:
            self.load_from_request_payload(payload)

        if refresh_token:
            self.load_from_refresh_token(refresh_token)

        if raw_json_str:
            self.load_from_request_payload(json.loads(raw_json_str.replace("'", "\"")))

        if not payload and not refresh_token and not raw_json_str:
            raise Exception('Token not properly initialized. You have to provide a single refresh token, or otherwise a dictionary/raw JSON string with the following shape: https://datatracker.ietf.org/doc/html/rfc6749#content.')


    def load_from_refresh_token(self, refresh_token):
        self.refresh_token = refresh_token
        self = self.refresh()

    def load_from_request_payload(self, payload):
        self.token = payload['access_token']
        self.refresh_token = payload['refresh_token']
        self.expiring = int(payload['expires_in'])
        self.start_time = time.time()
        self.payload = payload


    def expired(self):
        if elapsed_time(self.start_time) >= (self.expiring - 15): # If current time is above expiring time minus 10 seconds we ask for a new token.
            return True

        return False

    def refresh(self):
        token_endpoint = self.well_known['token_endpoint']

        body = {
            "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }

        resp = requests.post(token_endpoint, data=body)

        if resp.status_code != 200:
            craft_error_message(resp, token_endpoint)

        return Token(payload=resp.json(), well_known=self.well_known)

    def get_token(self):
        return self.token

    def __str__(self):
        return str(self.payload)

    def __repr__(self):
        return str(self.payload)

class OpenID:
    def __check_params(self, params):
        expected_params = ['password', 'username', 'grant_type', 'client_id']

        for param in expected_params:
            if param not in params:
                raise Exception("Missing parameter on OpenId class: ", param)


    def __init__(self, credentials, url=None):
        self.__check_params(credentials)

        if not url:
            raise Exception('URL Not Found: Make sure you provide a URL before invoking the service')

        self.credentials = credentials
        self.realm = self.credentials['realm']
        self.token = None
        self.url = url



    @staticmethod
    def createAdminClient(username=None, password=None, url = None):
        __props = {
            "client_id": "admin-cli",
            "grant_type": "password",
            "realm": "master",
            "username": username,
            "password": password
        }

        return OpenID(__props, url)

    def getToken(self):
        url = self.url
        well_known = get_well_known_info(url, self.realm)
        resp = requests.post(well_known['token_endpoint'], data=self.credentials)

        if resp.status_code == 200:
            payload = resp.json()
            return Token(payload=payload, well_known=well_known)
        else:
            craft_error_message(resp, url)
