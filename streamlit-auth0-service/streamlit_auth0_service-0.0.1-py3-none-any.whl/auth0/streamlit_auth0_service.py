import os

import requests
import streamlit as st

# from dotenv import load_dotenv
# load_dotenv('.env')

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_CLAIM_KEY = os.environ['AUTH0_CLAIM_KEY']


class StreamlitAuth0Service:

    def __init__(self):
        self.issuer_url = f'https://{AUTH0_DOMAIN}/'
        self.user_info_uri = f'{self.issuer_url}userinfo'

    def is_authorized(self, orgId="") -> bool:
        query_params = st.experimental_get_query_params()
        token = query_params.get("token")[0]
        user = self.get_user_info(token)

        if orgId is not None and len(orgId) > 0:
            return (user is not None
                    and user[AUTH0_CLAIM_KEY] is not None
                    and user[AUTH0_CLAIM_KEY]["user_metadata"]["org"] == orgId)
        else:
            return user is not None and user["email"] is not None

    def get_user_info(self, bearer_token: str) -> object:
        try:
            headers = {'Authorization': f'Bearer {bearer_token}'}
            response = requests.get(self.user_info_uri, headers=headers)
        except Exception as e:
            print('Error getting user info: ', e)
            return None

        if response.status_code != 200:
            return None

        return response.json()
