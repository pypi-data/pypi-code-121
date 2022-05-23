# -*- encoding: utf-8 -*-
from github import Github
from github.GitRelease import GitRelease  # pylint: disable=unused-import
from github.Repository import Repository  # pylint: disable=unused-import


class GithubHandler:
    _organization = "primait"

    def __init__(self, tokens):
        self._client = Github(tokens.github)

    def get_repo(self, repo_name):
        return self._client.get_repo(f"{self._organization}/{repo_name}")

    def get_organization(self):
        return self._client.get_organization(self._organization)

    def get_user(self):
        return self._client.get_user()

    def create_pr(self, repo, branch, title, body="", base="master", is_draft=False):
        return self.get_repo(repo).create_pull(
            title=title, head=branch, base=base, body=body, draft=is_draft
        )

    def get_pr(self, repo, pr_number):
        return self.get_repo(repo).get_pull(pr_number)

    def get_branch_from_pr(self, repo, pr_number):
        repo = self.get_repo(repo)
        return repo.get_branch(repo.get_pull(pr_number).head.ref)

    def get_tags(self, repo):
        return self.get_repo(repo).get_tags()

    def get_team_members(self, team_name=""):
        return self.get_organization().get_team_by_slug(team_name).get_members()

    def get_all_users(self):
        return self.get_organization().get_members()

    def get_list_pr(self, repo):
        pulls = self.get_repo(repo).get_pulls(
            state="open", sort="created", base="master"
        )
        return pulls

    def get_pr_from_branch(self, repo, branch):
        return self.get_repo(repo).get_pulls(head=f"primait:{branch}")

    def get_link_from_pr(self, repo, pr_number):
        return f"https://github.com/primait/{repo}/pull/{pr_number}"

    def get_commits_since_release(self, repo, tag):
        release_commit = repo.get_commit(tag)
        commits = []
        for c in repo.get_commits():
            if c == release_commit:
                break
            commits.append(c)
        return commits

    def get_latest_release_if_exists(self, repo):
        try:
            return repo.get_latest_release()
        except Exception:
            return None

    def user_is_admin(self, repo):
        return self.get_repo(repo).permissions.admin

    def get_release_if_exists(self, repo, release):
        try:
            return repo.get_release(release)
        except Exception:
            return None

    def get_build_status(self, repo, ref):
        return self.get_repo(repo).get_commit(ref).get_combined_status()

    def get_releases(self, repo):
        return self.get_repo(repo).get_releases()

    def get_branches(self, repo):
        return self.get_repo(repo).get_branches()

    def get_raw_content(self, repo, ref, file):
        repo = self.get_repo(repo)
        content = repo.get_contents(file, ref)
        return content.decoded_content
