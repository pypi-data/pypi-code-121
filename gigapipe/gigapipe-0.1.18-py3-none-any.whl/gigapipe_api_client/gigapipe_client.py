from gigapipe.api_client.api import Users, Organizations
from gigapipe.api_client.api.invites import Invites
from gigapipe.api_client.api.roles import Roles
from gigapipe.api_client.gigapipe_api import GigapipeApi


class GigapipeClient(object):
    """
    Gigapipe Python Client
    """

    def __init__(self, url: str = "https://api.gigapipe.com", *, client_id: str):
        """
        GigapipeClient Constructor
        :param url: URL of the api
        :param client_id: The Gigapipe Client ID
        """
        self.api = GigapipeApi(url, client_id=client_id)

        # Client Objects
        self.__users = Users(self.api)
        self.__organizations = Organizations(self.api)
        self.__invites = Invites(self.api)
        self.__roles = Roles(self.api)

    @property
    def users(self):
        """
        Users instance
        :return: The instance that handles all the user-related calls
        """
        return self.__users

    @property
    def organizations(self):
        """
        Organizations instance
        :return: The instance that handles all the organization-related calls
        """
        return self.__organizations

    @property
    def invites(self):
        """
        Invites instance
        :return: The instance that handles all the invites-related calls
        """
        return self.__invites

    @property
    def roles(self):
        """
        Roles instance
        :return: The instance that handles all the roles-related calls
        """
        return self.__roles

