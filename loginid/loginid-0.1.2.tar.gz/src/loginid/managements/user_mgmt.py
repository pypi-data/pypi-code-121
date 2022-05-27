from distutils.log import Log
from .. import LoginID


class _UserManagement():
    """
    User management class.
    """

    def get_user(self: LoginID, username: str) -> dict:
        """Get the user ID from username

        Args:
            username (str): The username

        Returns:
            dict: the user profile if no errors

        Raises:
            LoginIDError: If there is an error
        """
        url = "/manage/users/retrieve"

        payload = {
            "username": username
        }

        return self._request('post', url, "users.retrieve", payload)

    def delete_by_username(self: LoginID, username: str) -> str:
        """Delete a User by the username

        Args:
            username (str): the username to be deleted

        Returns:
            str: success message if user deleted successfully

        Raises:
            LoginIDError: If there is an error
        """
        url = "/manage/users/delete"

        payload = {
            "username": username
        }

        r = self._request('post', url, "users.delete", payload, expect=204)

        return f"User {username} deleted"

    def delete_by_user_id(self: LoginID, user_id: str) -> dict:
        """Delete a user by user Id

        Args:
            user_id (str): the user id to be deleted

        Returns:
            str: success message if user deleted successfully

        Raises:
            LoginIDError: If there is an error
        """
        url = f"/manage/users/{user_id}"

        self._request(
            'delete', url, token_scope="users.delete", expect=204)

        return f'user with id {user_id} deleted'

    def activate_user_by_id(self: LoginID, user_id: str) -> dict:
        """Activate a previously deactivated user

        Args:
            user_id (str): the user id to be activated

        Returns:
            dict: user profiles

        Raises:
            LoginIDError: If there is an error
        """
        url = f"/manage/users/{user_id}/activate"

        return self._request('put', url, token_scope="users.activate")

    def deactivate_user_by_id(self: LoginID, user_id: str) -> dict:
        """Deactivate a currently active user

        Args:
            user_id (str): the user id to be deactivated

        Returns:
            dict: user profiles if no error

        Raises:
            LoginIDError: If there is an error
        """
        url = f"/manage/users/{user_id}/deactivate"

        return self._request('put', url, token_scope="users.deactivate")

    def add_user_without_credentials(self: LoginID, username: str) -> dict:
        """Add a new user without credentials. The new user can create new credentials with recovery flow

        Args:
            username (str): The username of the new user

        Returns:
            dict: The new user's profile

        Raises:
            LoginIDError: If there is an error
        """
        url = f'/manage/users'

        payload = {
            "username": username
        }

        return self._request('post', url, "users.create", payload)
