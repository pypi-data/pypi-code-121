from glapi import configuration
from glapi.connection import GitlabConnection
from glapi.issue import GitlabIssue

class GitlabProject:
    """
    GitlabProject is a Gitlab Project.
    """

    def __init__(self, id: str = None, project: dict = None, event_actions: list = None, get_members: bool = False, get_events: bool = False, token :str = configuration.GITLAB_TOKEN, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            event_actions (list): strings of Gitlab User contribution types https://docs.gitlab.com/ee/user/index.html#user-contribution-events
            get_events (bool): TRUE if should pull events
            get_members (bool): TRUE if should pull user membership
            id (string): GitLab Project id
            project (dictionary): GitLab Project
            token (string): GitLab personal access or deploy token
            version (string): GitLab API version as base url
        """
        print(event_actions)
        self.connection = GitlabConnection(
            token=token,
            version=version
        )
        self.gitlab_type = "project"
        self.project = project if project else (self.connection.query("projects/%s" % id)["data"] if id and token and version else None)
        self.id = self.project["id"] if self.project else None
        self.events = self.extract_events(actions=event_actions) if get_events else None
        self.membership = self.extract_members() if get_members else None

    def extract_events(self, actions: list, date_start: str = None, date_end: str = None) -> dict:
        """
        Extract project-specific event data.

        Args:
            actions (list): enums where each represent an event action type https://docs.gitlab.com/ee/user/index.html#user-contribution-events
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value

        Returns:
            A dictionary where keys are event action types and corresponding values are lists of dictionaries where each represents a GitLab Event.
        """

        result = list()

        # check for connection ready
        if self.id and self.connection.token and self.connection.version:

            # loop through actions
            for action in actions:

                # check params
                if date_start or date_end or actions: params = dict()
                if date_end: params["created_before"] = date_end
                if date_start: params["created_after"] = date_start

                # update for action
                params["action"] = action

                # get events
                result += self.connection.paginate(
                    endpoint="projects/%s/events" % self.id,
                    params=params
                )

        return result if result else None

    def extract_issues(self, scope: str = "all", date_start: str = None, date_end: str = None) -> list:
        """
        Extract project-specific issue data.

        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value
            scope (enum): all | assigned_to_me | created_by_me

        Returns:
            A list of dictionaries where each represents a GtiLab Issue.
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
            issues = self.connection.paginate(
                endpoint="projects/%s/issues" % self.id,
                params=params
            )

            # generate GitlabIssue
            result = [GitlabIssue(issue=d) for d in issues]

        return result

    def extract_members(self) -> list:
        """
        Extract project-specific member data.

        Returns:
            A list of dictionaries where each represents a GtiLab User.
        """

        result = None

        # check connection params
        if self.id and self.connection.token and self.connection.version:

            # query api
            result = self.connection.paginate(
                endpoint="projects/%s/members" % self.id
            )

        return result
