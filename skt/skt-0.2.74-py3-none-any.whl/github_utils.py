import base64

from github import Github, GithubException
from contextlib import contextmanager


@contextmanager
def proxy(proxies):
    import os

    env_backup = dict(os.environ)
    os.environ["HTTP_PROXY"] = proxies["http"]
    os.environ["HTTPS_PROXY"] = proxies["https"]
    yield
    os.environ.clear()
    os.environ.update(env_backup)


class GithubUtil:
    def __init__(self, token, proxies=None):
        self._token = token
        self._proxies = proxies

    def query_gql(self, gql):
        import requests
        import json

        endpoint = "https://api.github.com/graphql"
        data = json.dumps({"query": gql})
        headers = {"Authorization": f"Bearer {self._token}"}

        return requests.post(endpoint, data=data, headers=headers, proxies=self._proxies).json()

    def check_path_from_git(self, path) -> bool:
        return path.startswith("https://github.com/")

    def _download_from_git(self, path) -> bytes:
        splited = path.split("/")
        org_name = splited[3]
        repo_name = splited[4]
        ref_name = splited[6]
        target_path = "/".join(splited[7:])

        g = Github(self._token)

        org = g.get_organization(org_name)
        repo = org.get_repo(repo_name)
        content = repo.get_contents(target_path, ref=ref_name)
        file_sha = content.sha
        blob = repo.get_git_blob(file_sha)
        file_data = base64.b64decode(blob.raw_data["content"])

        return file_data

    def download_from_git(self, path) -> bytes:
        if self._proxies:
            with proxy(self._proxies):
                file_data = self._download_from_git(path)
        else:
            file_data = self._download_from_git(path)

        return file_data

    def _download(self, org_id, repo_id, ref_id, path) -> bytes:
        g = Github(self._token)
        org = g.get_organization(org_id)
        repo = org.get_repo(repo_id)
        try:
            content = repo.get_contents(path, ref=ref_id)
            return content.decoded_content
        except GithubException as e:
            if e.status == 403:
                if e.data["errors"][0]["code"] == "too_large":
                    parent_path = path[: path.rfind("/")]
                    contents = repo.get_contents(parent_path, ref=ref_id)
                    for c in contents:
                        if c.path == path:
                            blob = repo.get_git_blob(c.sha)
                            return base64.b64decode(blob.raw_data["content"])
            raise e

    def download(self, org_id, repo_id, ref_id, path) -> bytes:
        if self._proxies:
            with proxy(self._proxies):
                file_data = self._download(org_id, repo_id, ref_id, path)
        else:
            file_data = self._download(org_id, repo_id, ref_id, path)

        return file_data

    def _parse_url(self, url):
        from urllib.parse import urlparse

        parse_result = urlparse(url)
        if parse_result.netloc == "github.com":
            splits = parse_result.path.split("/")
            org_id = splits[1]
            repo_id = splits[2]
            ref_id = splits[4]
            path = "/".join(splits[5:])

        return org_id, repo_id, ref_id, path

    def download_from_url(self, url) -> bytes:
        ret = self._parse_url(url)

        return self.download(*ret)
