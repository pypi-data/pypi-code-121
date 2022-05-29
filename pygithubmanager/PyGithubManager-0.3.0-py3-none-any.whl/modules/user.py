import pygit2 as pygit2
from github.AuthenticatedUser import AuthenticatedUser
from github.NamedUser import NamedUser
from github.PaginatedList import PaginatedList


class User:
    def __init__(self, github, user, token):
        """
        Initializes the user object.

        Parameters
        ----------
        github : Github
            Github object.
        user : AuthenticatedUser
            Authenticated user.
        token : str
            Token of the authenticated user.
        """
        self.github = github
        self.user: AuthenticatedUser = user
        self.named_user: NamedUser = self.github.get_user(self.user.login)
        self.repos = None
        self.token = token
        self.pygit_callback = pygit2.RemoteCallbacks(pygit2.UserPass(token, 'x-oauth-basic'))

    def generate_repos(self):
        """
        Generates a list of repositories for the authenticated user.

        Returns
        -------
        bool
            True if the list of repositories was generated successfully.
        """
        check = False
        if self.user is not None:
            self.repos: PaginatedList = self.user.get_repos()
            check = True
        return check

    def get_repos(self):
        """
        Returns the list of repositories for the authenticated user.

        Returns
        -------
        PaginatedList
            List of repositories.
        """
        check = None
        if self.repos is None:
            if self.generate_repos():
                check = self.repos
        else:
            check = self.repos
        return check

    def get_data(self):
        """
        Returns the data of the authenticated user.

        Returns
        -------
        AuthenticatedUser
            Data of the authenticated user.
        """
        return self.user

    def get_named_user_data(self):
        """
        Returns the data of the named user.

        Returns
        -------
        NamedUser
            Data of the named user.
        """
        return self.named_user
