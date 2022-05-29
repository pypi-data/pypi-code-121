import requests
import json


class GotifyNotification:
    """Basic gotify notification class

    :param url: gotify server url
    :type url: str
    :param app_token: token to which application send a message
    :type app_token: str
    :param title: title of the message
    :type title: str
    :param message: message
    :type message: str
    :param priority: message priority, defaults to 5
    :type priority: int, optional
    """

    CONTENT_TYPE = 'plain'

    def __init__(
        self,
        url,
        app_token: str,
        title: str = None,
        message: str = None,
        priority: int = 5
    ):
        """Constructor method"""

        self.url = url + '/message'
        self.headers = {
            "X-Gotify-Key": app_token,
            "Content-type": 'application/json'
        }
        self.payload = {
            "title": title,
            "priority": priority,
            "message": message,
            "extras": {
                "client::display": {
                     "contentType": "text/"+self.CONTENT_TYPE
                }
            }
        }
        self.delivered = False

    def send(self,
             message: str = None,
             title: str = None,
             priority: int = None) -> requests.models.Response:
        """sends message to gotify server

        :param title: title of the message
        :type title: str
        :param message: message
        :type message: str
        :param priority: message priority, defaults to 5
        :type priority: int, optional
        :return: _description_
        :rtype: response.Request
        """

        if message:
            self.payload['message'] = message
        if title:
            self.payload['title'] = title
        if priority:
            self.payload['priority'] = priority

        response = requests.post(
            self.url,
            headers=self.headers,
            json=self.payload
        )
        if response.ok:
            self.delivered = True
        return response

    @property
    def json(self) -> str:
        """property shows constructed object in string json format`

        :return: constructed object in string json format
        :rtype: str
        """
        return json.dumps(self.__dict__, indent=4)
