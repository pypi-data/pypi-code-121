"""
Resource 
"""
import requests
from typing import Dict


class Response(object):
    def __init__(self, data, success, error_message: str = None):
        self.data = data
        self.success = success
        self.error_message = error_message


class RequestClient(object):

    def __init__(self, api_key, api_base, api_version):
        self.api_key = api_key
        self.api_base = api_base
        self.api_version = api_version
        self._create_session()

    def _create_session(self):
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=100, pool_maxsize=100
        )
        # Test Mode
        if self.api_base.startswith('http://'):
            self.session.mount('http://', adapter)
        else:
            self.session.mount('https://', adapter)

    def build_request(
        self,
        method,
        url,
        params=None
    ):
        """
        Constructing request
        """

        if self.api_key is None:
            raise ValueError("No API key provided")

        rheaders = self.build_headers(
            api_key=self.api_key,
            method=method
        )

        # Build URL
        rurl = f"{self.api_base.rstrip('/')}/{self.api_version}/{url}/"

        return rurl, rheaders

    def build_headers(self, api_key: str, method: str) -> Dict:
        """Constructing request headers"""
        if method in ("post", "put", "delete"):
            return {
                'Authorization': f'Token {api_key}',
                'Content-Type': 'application/json'
            }
        return {'Authorization': f'Token {api_key}'}

    def get(self, url: str, params=None):
        rurl, rheaders = self.build_request(method="get", url=url)
        response = self.session.get(
            url=rurl, headers=rheaders, params=params
        )
        
        if response.status_code == 200:
            return Response(data=response.json(), success=True)
        
        return Response(data={}, success=False, error_message=response.text)

    def post(self, url: str, data: Dict):
        rurl, rheaders = self.build_request(method="post", url=url)
        response = self.session.post(
            url=rurl, headers=rheaders, data=data
        )
        
        if response.status_code == 200:
            return Response(data=response.json(), success=True)
        
        return Response(data={}, success=False, error_message=response.text)

    def put(self, url: str, data: Dict):
        rurl, rheaders = self.build_request(method="put", url=url)
        response = self.session.put(
            url=rurl, headers=rheaders, data=data
        )
        
        if response.status_code == 200:
            return Response(data=response.json(), success=True)
        
        return Response(data={}, success=False, error_message=response.text)

    def delete(self, url: str, data: Dict):
        rurl, rheaders = self.build_request(method="delete", url=url)
        response = self.session.delete(
            url=rurl, headers=rheaders, data=data
        )
        
        if response.status_code == 200:
            return Response(data=response.json(), success=True)
       
        return Response(data={}, success=False, error_message=response.text)
