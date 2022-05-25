from gigapipe.api_client.api import (
    Users,
    Organizations,
    Invites,
    Roles,
    Root,
    Clusters,
    Clickhouse,
    Imports,
    Integrations
)
from gigapipe.api_client.gigapipe_api import GigapipeApi


class GigapipeClient(object):
    """
    Gigapipe Python Client
    """

    gigapipe_url: str = "https://api.gigapipe.com"

    def __init__(self, client_id: str):
        """
        GigapipeClient Constructor
        :param client_id: The Gigapipe Client ID
        """
        self.api = GigapipeApi(self.__class__.gigapipe_url, client_id=client_id)

        # Client Objects
        self.__root = Root(self.api)
        self.__users = Users(self.api)
        self.__organizations = Organizations(self.api)
        self.__invites = Invites(self.api)
        self.__roles = Roles(self.api)
        self.__clusters = Clusters(self.api)
        self.__clickhouse = Clickhouse(self.api)
        self.__imports = Imports(self.api)
        self.__integrations = Integrations(self.api)

    @property
    def root(self):
        """
        Root instance
        :return: The instance that handles all the root-related calls
        """
        return self.__root

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

    @property
    def clusters(self):
        """
        Clusters instance
        :return: The instance that handles all the clusters-related calls
        """
        return self.__clusters

    @property
    def clickhouse(self):
        """
        Clickhouse instance
        :return: The instance that handles all the clickhouse-related calls
        """
        return self.__clickhouse

    @property
    def imports(self):
        """
        Imports instance
        :return: The instance that handles all the clickhouse-related calls
        """
        return self.__imports

    @property
    def integrations(self):
        """
        Integrations instance
        :return: The instance that handles all the clickhouse-related calls
        """
        return self.__integrations

