from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


class FetchService():

    def __init__(self):
        pass

    def fetch_json(self, endpoint: str, parameters, headers) -> dict: 
        """
        Fetch JSON data from an endpoint

        Args:
            endpoint: the endpoint to fetch from
            parameters: the parameters to pass to the endpoint
            headers: the headers to pass to the endpoint
        
        Returns:
            The JSON data as a dict

        Raises:
            HTTPException: if the connection fails
        """
        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(endpoint, params=parameters)
            data = json.loads(response.text)
            return data
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            raise
  