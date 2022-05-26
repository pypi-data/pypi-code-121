import os

import requests
import streamlit as st

# from dotenv import load_dotenv
# load_dotenv('.env')

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_CLAIM_KEY = os.environ['AUTH0_CLAIM_KEY']
ORG_ID = os.environ.get('ORG_ID')


class StreamlitAuth0Service:

    def __init__(self):
        self.issuer_url = f'https://{AUTH0_DOMAIN}/'
        self.user_info_uri = f'{self.issuer_url}userinfo'

    def is_authorized(self, org_id="") -> bool:
        query_params = st.experimental_get_query_params()
        token = query_params.get('token')
        if token is None or len(token) <= 0:
            return False

        user = self.get_user_info(token[0])
        org_id = self.get_org_id(org_id)

        if org_id is not None and len(org_id) > 0:
            return (user is not None
                    and user[AUTH0_CLAIM_KEY] is not None
                    and user[AUTH0_CLAIM_KEY]["user_metadata"]["org"] == org_id)
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

    def get_org_id(self, org_id):
        if org_id is None or len(org_id) == 0:
            return ORG_ID
        else:
            return org_id
