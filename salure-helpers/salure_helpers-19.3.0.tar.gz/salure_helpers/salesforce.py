import urllib.parse
import requests
import json
from typing import Union, List


class Salesforce(object):
    """
    This class is meant to be a simple wrapper around the Salesforce API. In order to start using it, authorize your application is Salureconnect.
    You will receive a code which you can use to obtain a refresh token using the get_refresh_token method. Use this refresh token to refresh your access token always before you make a data call.
    """
    def __init__(self, customer_url: str, client_id: str, client_secret: str, redirect_uri: str = None,):
        self.customer_url = customer_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = 'https://salureconnect.com/api/manage/connectors/oauth2/salesforce' if redirect_uri is None else redirect_uri
        self.access_token = ''

    def get_refresh_token(self, authorization_code: str) -> requests.Response:
        """
        This method is for one time use. After obtaining the code from SalureConnect, this method is used to get a refresh token.
        :param authorization_code: code you obtained from SalureConnect after going through the OAuth flow
        :return: json with refresh token
        """
        params = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": authorization_code
        }
        response = requests.get(url="https://login.salesforce.com/services/oauth2/token?", params=params)

        return response

    def refresh_access_token(self, refresh_token: str):
        """
        This method can be used to get a new access_token
        :param refresh_token: refresh token you have obtained from the get_refresh_token method
        :return: nothing. Access property in class is set to latest access token
        """
        params = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": refresh_token
        }
        response = requests.get(url="https://login.salesforce.com/services/oauth2/token?", params=params)
        if 300 > response.status_code >= 200:
            self.access_token = response.json()['access_token']
        else:
            print(f"There was a problem getting the access token. Response is: {response}")

    def query_data(self, query: str) -> requests.Response:
        """
        This method is used to send raw queries to Salesforce.
        :param query: Querystring. Something like: 'select+Name,Id+from+Account'
        :return: data or error
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "q": query
        }
        params_str = urllib.parse.urlencode(params, safe=':+')
        response = requests.request(method="GET", url=f"{self.customer_url}services/data/v37.0/query/?", params=params_str, headers=headers)

        return response

    def get_data(self, fields: Union[str, List], object_name: str, filter: str = None) -> requests.Response:
        """
        This method is used to send queries in a somewhat userfriendly wayt to Salesforce.
        :param fields: fields you want to get
        :param object_name: table or object name that the fields need to be retrieved from
        :param filter: statement that evaluates to True or False
        :return: data or error
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        fields = ",".join(fields) if isinstance(fields, List) else fields
        params = {
            "q": f"SELECT {fields} FROM {object_name}{' WHERE ' + filter if filter is not None else ''}"
        }
        params_str = urllib.parse.urlencode(params, safe=':+')

        response = requests.get(url=f"{self.customer_url}services/data/v37.0/query/?", params=params_str, headers=headers)

        return response
