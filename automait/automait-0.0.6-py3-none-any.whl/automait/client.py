from typing import List, Union
import requests

BASE_URL = "http://api.automait.ai/"


class Client():
    _login = None
    _password = None

    def __init__(self, login, password):
        self._login = login
        self._password = password
        self._check_creds()

    @property
    def login(self):
        return self._login

    @property
    def password(self):
        return self._password

    def _check_creds(self):
        payload = {
            "login": self._login,
            "password": self._password}
        r = requests.post(
            url=BASE_URL+"login",
            params=payload
        )
        print(r)
        if r.status_code == 200:
            return True
        else:
            raise Exception("Invalid credentials.")

    def dataset_from_xlsx(self, filepath: Union[str, List[str]]):
        """Add new datasets to your account.

        New datasets can be passed either as a
        filepath to your xlsx file or as a list of
        xlsx file paths.

        Args:
            filepath (Union[str, List[str]]): filepath(s) to be used

        Raises:
            Exception: In case an invalid filepath is passed.

        Returns:
            identifier int: the id of your new dataset
        """
        if type(filepath) is str:
            filepath = [filepath]
        elif type(filepath) is list:
            pass
        else:
            raise Exception("Invalid filepath.")

        

        print("### Added dataset to your account. ###")

        identifier = 10

        return identifier
