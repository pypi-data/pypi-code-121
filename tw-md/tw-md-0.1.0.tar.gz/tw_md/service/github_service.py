import json
from typing import List

import requests

from ..domain.commit import Commit
from ..domain.repository import Repository
from ..errors.github_errors import RepositoryNotFoundError


class GithubService:
    def __init__(self) -> None:
        self.__base_url = "https://api.github.com"

    def get_repository(self, name: str, owner: str) -> Repository:
        commits = self.__get_repository_commits(owner, name)
        return Repository(name, owner, commits)

    def __get_repository_commits(self, owner: str, repository: str) -> List[Commit]:
        url = f"{self.__base_url}/repos/{owner}/{repository}/commits"
        response = requests.get(url)
        if response.status_code == 404:
            raise RepositoryNotFoundError()
        response_body = json.loads(response.text)
        return [
            Commit(commit["sha"], commit["commit"]["message"])
            for commit in response_body
        ]
