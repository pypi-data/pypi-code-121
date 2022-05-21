from glapi import configuration
from glapi.connection import GitlabConnection
from glapi.issue import GitlabIssue

class GitlabEpic:
    """
    GitlabEpic is a Gitlab Epic.
    """

    def __init__(self, id: str = None, iid: str = None, epic: dict = None, group_id: str = None, group_users: list = None, issues: list = None, notes: list = None, get_issues: bool = False, get_notes: bool = False, get_participants: bool = False, token :str = configuration.GITLAB_TOKEN, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            id (string): GitLab Epic id
            iid (string): GitLab Epic iid
            issues (list): classes of GitLabIssue
            epic (dictionary): GitLab Epic
            get_issues (boolean): TRUE if issues should be pulled
            get_notes (boolean): TRUE if notes should be pulled
            get_participants (boolean): TRUE if issue participants should be pulled
            group_id (string): Gitlab Group id
            group_users (list): classes of GitlabUser
            notes (list): dictionaries of GitLab notes (comments)
            token (string): GitLab personal access, ci, or deploy token
            version (string): GitLab API version as base url
        """
        self.connection = GitlabConnection(
            token=token,
            version=version
        )
        self.epic = epic if epic else (self.connection.query("groups/%s/epics/%s" % (group_id, iid))["data"] if id and token and version else None)
        self.gitlab_type = "epic"
        self.group_id = self.epic["group_id"] if self.epic else None
        self.group_users = group_users
        self.id = self.epic["id"] if self.epic else None
        self.iid = self.epic["iid"] if self.epic else None
        self.issues = self.extract_issues() if get_issues else issues
        self.notes = notes if notes else (self.extract_notes() if get_notes else None)
        self.participants = self.extract_participants() if get_participants else None

    def extract_issues(self, scope: str = "all", date_start: str = None, date_end: str = None) -> list:
        """
        Extract epic-specific issue data.

        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value
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
            issues = self.connection.paginate(
                endpoint="groups/%s/epics/%s/issues" % (
                    self.group_id,
                    self.iid
                ),
                params=params
            )

            # generate GitlabIssue
            result = [GitlabIssue(issue=d, token=self.connection.token, version=self.connection.version) for d in issues]

        return result

    def extract_notes(self) -> list:
        """
        Extract epic-specific note data (comments).

        Returns:
            A list of dictionaries where each represents a GtiLab Note.
        """

        result = None

        # check connection params
        if self.id and self.connection.token and self.connection.version:

            # query api
            result = self.connection.paginate(
                endpoint="groups/%s/epics/%s/notes" % (
                    self.group_id,
                    self.id
                )
            )

        return result

    def extract_participants(self) -> list:
        """
        Extract epic-specific participants based on issue partificpants or @mentions.

        Returns:
            A list of dictionaries where each represents a Gitlab user.
        """

        result = None
        issue_participants = None
        mentions_as_participants = None
        author_as_participant = [self.epic["author"]] if self.epic else None

        # check for issues
        if self.issues:

            # pull participants, flatten, and dedup
            issue_participants = [
                dict(t) for t in {
                    tuple(z.items()) for z in [
                        x for y in [
                            d.extract_participants() for d in self.issues
                        ] for x in y
                    ]
                }
            ]

        # check notes
        if self.notes and self.group_users:

            # try to pull @mentions from notes
            mentions_as_participants = [
                dict(t) for t in { tuple(z.items()) for z in [
                        x for y in [
                            [u.user for u in self.group_users if "@%s" % u.user["username"] in d["body"]]
                            for d in self.notes
                            if any("@%s" % u.user["username"] in d["body"] for u in self.group_users)
                        ] for x in y
                    ]
                }
            ]

            # delete keys so downstream dedup works
            for d in mentions_as_participants:
                del d["access_level"]
                del d["created_at"]
                del d["expires_at"]

        # update result
        result = issue_participants if issue_participants else list()
        result = author_as_participant if result is None else result
        result = mentions_as_participants if result is None else (result + mentions_as_participants if mentions_as_participants else result)

        # dedup one last time post merge
        return [ dict(t) for t in {tuple(d.items()) for d in result } ]
