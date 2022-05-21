import requests
import json
from qplay_cli.config.qplay_config import QplayConfig

class UserAPIClient:

    BASE_PROD_URL = 'https://s5y92z0788.execute-api.ap-south-1.amazonaws.com/prod'

    def __init__(self):
        pass

    def get_info(self, access_token):
        x = requests.post(
            UserAPIClient.BASE_PROD_URL + "/info",
            data=json.dumps(
                {
                    'access_token': access_token

                }))
        response = json.loads(x.text)

        if response['error'] == True:
            print(response['message'])
            quit()

        return response


    def signup(self, username, name, email, password):
        x = requests.post(
            UserAPIClient.BASE_PROD_URL + "/signup",
            data=json.dumps(
                {
                    'username': username,
                    'password': password,
                    "email": email,
                    "name": name

                }))
        response = json.loads(x.text)

        if response['error'] == True:
            print(response['message'])
            quit()

        return response

    def confirm_signup(self, username, password, code):
        x = requests.post(
            UserAPIClient.BASE_PROD_URL + "/confirm_signup",
            data=json.dumps(
                {
                    'username': username,
                    'password': password,
                    "code": code

                }))
        response = json.loads(x.text)

        if response['error'] == True:
            print(response['message'])
            quit()

        return response

    def signin(self, username, password):
        x = requests.post(UserAPIClient.BASE_PROD_URL + "/signin", data=json.dumps({'username': username, 'password': password}))
        access_token = json.loads(x.text)['data']['access_token']
        QplayConfig.save_credentials(access_token)
