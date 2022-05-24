
import json
import requests
from datetime import datetime
from daspython.common.api import Token

class DasAuth(Token):
    '''This object represents the authenticator to the DAS API and keeps your token.'''

    def __init__(self, base_url, username, password):
        '''
        Parameters
        ----------
        base_url: str
            DAS API address.
        username: str
            A valid DAS account.            
        password: str
            Password from the given account.
        '''
        self.api_url_base = base_url
        self.username = username
        self.password = password
        self.check_https = True


    def authenticate(self, check_https=True):
        '''
        Authenticates based on the given credentials against the given DAS API address when a new instance was created.

        Parameters
        ----------
        check_https: boolean, default: True
            Use this flag to debuggind and test only and set to False if applicable when the given DAS API address has no certificate.
        '''
        
        self.check_https = check_https
        api_url = '{0}/api/TokenAuth/Authenticate'.format(self.api_url_base)

        data = json.dumps({
            'userNameOrEmailAddress': self.username,
            'password': self.password
        })

        response = requests.post(
            url=api_url, headers=self.headers, data=data, verify=check_https)

        self.username = None
        self.password = None            

        if response.status_code == 200:
            result = json.loads(response.content.decode('utf-8'))
            self.api_token = result['result']['accessToken']
            self.expireInSeconds = int(result['result']['expireInSeconds'])

            self.headers = {'Content-Type': 'application/json',
                            'Authorization': 'Bearer {0}'.format(self.api_token)}
            return True
        else:
            return False
