from glapi import configuration
from glapi.connection import GitlabConnection

class GitlabIssue:
    """
    GitlabIssue is a GitLab Issue.
    """

    def __init__(self, id: str = None, issue: dict = None, notes: list = None, get_links: bool = False, get_notes: bool = False, get_participants: bool = False, token :str = configuration.GITLAB_TOKEN, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            id (string): GitLab Issue id
            get_links (boolean): TRUE if links should be pulled
            get_notes (boolean): TRUE if notes should be pulled
            get_participants (boolean): TRUE if participants should be pulled
            issue (dict): key/values representing a Gitlab Issue
            notes (list): dictionaries of GitLab notes (comments)
            token (string): GitLab personal access or deploy token
            version (string): GitLab API version as base url
        """
        self.connection = GitlabConnection(
            token=token,
            version=version
        )
        self.gitlab_type = "issue"
        self.issue = issue if issue else self.connection.query("issues/%s" % id)["data"]
        self.id = self.issue["id"] if self.issue else None
        self.iid = self.issue["iid"] if self.issue else None
        self.project_id = self.issue["project_id"] if self.issue else None
        self.links = self.extract_links() if get_links else None
        self.notes = notes if notes else (self.extract_notes() if get_notes else None)
        self.participants = self.extract_participants() if get_participants else None

    def extract_links(self) -> list:
        """
        Extract issue-specific link data (relates to, blocks, is blocked by).

        Returns:
            A list of dictionaries where each represents a GitLab Issue.
        """

        result = None

        # check connection params
        if self.iid and self.connection.token and self.connection.version:

            # query api
            result = self.connection.query(
                endpoint="projects/%s/issues/%s/links" % (
                    self.project_id,
                    self.iid
                )
            )["data"]

        return result

    def extract_notes(self) -> list:
        """
        Extract issue-specific note data (comments).

        Returns:
            A list of dictionaries where each represents a GtiLab Note.
        """

        result = None

        # check connection params
        if self.iid and self.connection.token and self.connection.version:

            # query api
            result = self.connection.paginate(
                endpoint="projects/%s/issues/%s/notes" % (
                    self.project_id,
                    self.iid
                )
            )

        return result

    def extract_participants(self) -> list:
        """
        Extract issue-specific participant data.

        Returns:
            A list of dictionaries where each represents a GitLab User.
        """

        result = None

        # check connection params
        if self.iid and self.connection.token and self.connection.version:

            # query api
            r = self.connection.paginate(
                endpoint="projects/%s/issues/%s/participants" % (
                    self.project_id,
                    self.iid
                )
            )

            # remove author as participant
            result = [d for d in r if d["id"] != self.issue["author"]["id"]]

        return result
