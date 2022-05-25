class AuthenticationFailed(Exception):
    """User was not authenticated."""

    def __init__(self):
        Exception.__init__(self, "User was not authenticated.")


class GrantNotProvided(Exception):
    """Grant was not provided."""

    def __init__(self, grant_name: str, dictionary_without_grant: dict):
        Exception.__init__(self, f"{grant_name} not provided within {dictionary_without_grant}.")
