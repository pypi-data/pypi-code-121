from optparse import Option
from .. import LoginID
from typing import Optional


class _CodeManagement():
    """
    Code management class.
    """

    def generate_code(self: LoginID, code_type: str,
                      code_purpose: str, is_authorized: bool,
                      user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        """Generate a code

        Args:
            code_type (str): The code type
            code_purpose (str): The purpose of the code
            is_authorized (bool): Whether the code authorizes the user or not
            user_id (str, optional): The user id to generate the code for. Defaults to None.
            username (str, optional): The username, must be present if `user_id` is not . Defaults to None.

        Returns:
            dict: the response body from code generation request if no errors, else raise LoginIDError
        """
        self.validate_code_type(code_type)

        url = f"/codes/{code_type}/generate"

        payload = dict(
            client_id=self._client_id,
            purpose=code_purpose,
            authorize=is_authorized
        )
        self._update_payload(payload, user_id, username)

        return self._request('post', url, "codes.generate", payload=payload)

    def authorize_code(self: LoginID, code: str,
                       code_type: str, code_purpose: str,
                       user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        """Authorize a given code

        Args:
            code (str): The code that needs authorization
            code_type (str): The type of the code
            code_purpose (str): The purpose of the code
            user_id (str, optional): The user_id associate with the code. Defaults to None.
            username (str, optional): The username, must be present if `user_id` is not . Defaults to None.

        Returns:
            dict: The response body from code authorization
        """
        self.validate_code_type(code_type)

        url = f"/codes/{code_type}/authorize"

        payload = dict(
            client_id=self._client_id,
            purpose=code_purpose,
            code=code
        )
        self._update_payload(payload, user_id, username)

        return self._request('post', url, "codes.authorize", payload=payload)

    def invalidate_all_codes(self: LoginID,
                             code_type: str, code_purpose: str,
                             user_id: Optional[str] = None, username: Optional[str] = None) -> dict:
        """Invalidate all codes of a given type

        Args:
            code_type (str): code type
            code_purpose (str): the purpose of the code
            user_id (str, optional): The user_id associate with the code. Defaults to None.
            username (str, optional): The username, must be present if `user_id` is not . Defaults to None.

        Returns:
            dict: The response body from code invalidation::

                {
                    "deleted_at": "2020-04-01T00:00:00.000Z",
                }

        Raises:
            LoginIDError: If there is an error
        """
        self.validate_code_type(code_type)

        url = f'/codes/{code_type}/invalidate-all'

        payload = dict(
            client_id=self._client_id,
            purpose=code_purpose,
        )
        self._update_payload(payload, user_id, username)

        return self._request('post', url, "codes.invalidate", payload=payload)
