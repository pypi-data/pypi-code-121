import datetime
import json
import typing as t

import requests
from requests import Response

DOCKER_DIGEST_HEADER = "Docker-Content-Digest"


class Registry:
    host: str
    proto: str

    def __init__(self, host, proto="http"):
        self.host = host
        self.proto = proto

    def list_repositories(self) -> t.List[str]:
        resp: Response = self._check_call(f"{self.proto}://{self.host}:5000/v2/_catalog")
        repos = resp.json()["repositories"]
        return repos

    def list_tags(self, repo: str) -> t.List[str]:
        resp: Response = self._check_call(f"{self.proto}://{self.host}:5000/v2/{repo}/tags/list")
        return resp.json()["tags"]

    def get_digest(self, repo: str, tag: str) -> str:
        resp: Response = self._check_call(f"{self.proto}://{self.host}:5000/v2/{repo}/manifests/{tag}", requests.get,
                                          headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"})
        digest = resp.headers[DOCKER_DIGEST_HEADER]
        return digest

    def get_create_date(self, repo: str, tag: str) -> datetime.datetime:
        resp: Response = self._check_call(f"{self.proto}://{self.host}:5000/v2/{repo}/manifests/{tag}", requests.get,
                                          headers={"Accept": "application/vnd.docker.distribution.manifest.v1+json"})
        raw_dt = json.loads(resp.json()["history"][0]["v1Compatibility"])["created"]
        return datetime.datetime.strptime(raw_dt[:len("yyyy-mm-ddThh:mm:ss.ffffff")], "%Y-%m-%dT%H:%M:%S.%f")

    def delete_image(self, repo: str, digest: str):
        self._check_call(f"{self.proto}://{self.host}:5000/v2/{repo}/manifests/{digest}", requests.delete)

    def get_contents(self) -> t.Dict[str, t.List['DockerImage']]:
        contents = {}
        for repo in self.list_repositories():
            tags = self.list_tags(repo)
            images = []
            for tag in tags:
                images.append(DockerImage(repo, tag, self.get_digest(repo, tag), self.get_create_date(repo, tag)))
            contents[repo] = images

        return contents

    def _check_call(self, url, fn: t.Callable = requests.get, headers=None):
        resp: Response = fn(url, headers=headers)
        if not resp.ok:
            raise ValueError(f"Request to {url} had code: {resp.status_code}: {resp.text}")
        return resp


class DockerImage(t.NamedTuple):
    repo: str
    tag: str
    digest: str
    created: datetime.datetime