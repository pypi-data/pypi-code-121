from glapi import configuration
from glapi.connection import GitlabConnection

class GitlabGroup:
    """
    GitlabGroup is a Gitlab Group.
    """

    def __init__(self, id: str = None, group: dict = None, token :str = configuration.GITLAB_TOKEN, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            id (string): GitLab Project id
            group (dictionary): GitLab Group
            token (string): GitLab personal access or deploy token
            version (string): GitLab API version as base url
        """
        self.connection = GitlabConnection(
            token=token,
            version=version
        )
        self.group = group if group else (self.connection.query("groups/%s" % id)["data"] if id and token and version else None)
        self.id = self.group["id"] if self.group else None

    def extract_epics(self, date_start: str = None, date_end: str = None, group_users: list = None, get_issues: bool = False, get_notes: bool = False, get_participants: bool = False) -> list:
        """
        Extract group-specific epic data.

        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value
            get_issues (boolean): TRUE if issues should be pulled
            get_notes (boolean): TRUE if notes should be pulled
            get_participants (boolean): TRUE if participants should be pulled
            group_users (list): classes of GitlabUser

        Returns:
            A list of GitlabEpic classes where each represents a GtiLab Epic.
        """

        result = None
        params = dict()

        # check params
        if date_end: params["created_before"] = date_end
        if date_start: params["created_after"] = date_start

        # check connection params
        if self.id and self.connection.token and self.connection.version:

            # query api
            result = self.connection.paginate(
                endpoint="groups/%s/epics" % self.id,
                params=params
            )

        return result

    def extract_issues(self, scope: str = "all", date_start: str = None, date_end: str = None, get_notes: bool = False, get_links: bool = False, get_participants: bool = False) -> list:
        """
        Extract group-specific epic data.

        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value
            get_links (boolean): TRUE if links should be pulled
            get_notes (boolean): TRUE if notes should be pulled
            get_participants (boolean): TRUE if participants should be pulled
            scope (enum): all | assigned_to_me | created_by_me

        Returns:
            A list of GitlabIssue classes where each represents a GtiLab Issue.
        """

        result = None

        # check params
        if date_start or date_end or scope: params = dict()
        if date_end: params["created_before"] = date_end
        if date_start: params["created_after"] = date_start
        if scope: params["scope"] = scope

        # check connection params
        if self.id and self.connection.token and self.connection.version:

            # query api
            result = self.connection.paginate(
                endpoint="groups/%s/issues" % self.id,
                params=params
            )

        return result

    def extract_projects(self, date_start: str = None, date_end: str = None) -> list:
        """
        Extract group-specific project data.

        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value

        Returns:
            A list of GitlabProject classes where each represents a GtiLab Project.
        """

        result = None
        params = dict()

        # check params
        if date_start or date_end: params = dict()
        if date_end: params["created_before"] = date_end
        if date_start: params["created_after"] = date_start

        # check connection params
        if self.id and self.connection.token and self.connection.version:

            # query api
            result = self.connection.paginate(
                endpoint="groups/%s/projects" % self.id,
                params=params
            )

        return result

    def extract_users(self) -> list:
        """
        Extract group-specific user data.

        Returns:
            A list of GitlabUser classes where each represents a GtiLab User.
        """

        result = None

        # check connection params
        if self.id and self.connection.token and self.connection.version:

            # query api
            result = self.connection.paginate(
                endpoint="groups/%s/members" % self.id
            )

        return result
