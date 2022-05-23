# -*- encoding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from suite_py.lib.requests.auth import BearerAuth
from suite_py.lib.requests.session import Session

REGEX = r"([A-Za-z]+-[0-9]+)"


class YoutrackHandler:
    def __init__(self, config, tokens):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        self._base_url = config.youtrack["url"] + "/"
        self._issue_url = urljoin(self._base_url, "issue/")
        self._client = Session(base_url=urljoin(self._base_url, "api/"))
        self._client.headers = headers
        self._client.auth = BearerAuth(tokens.youtrack)

    def get_projects(self):
        params = {"fields": "id,name,shortName"}
        return self._client.get("admin/projects", params=params).json()

    def get_current_user(self):
        params = {"fields": "login"}
        return self._client.get("users/me", params=params).json()

    def get_issue(self, issue_id):
        params = {
            "fields": "$type,id,idReadable,summary,customFields(name,value(name))"
        }
        issue = self._client.get(f"issues/{issue_id}", params=params).json()
        type_field = [x for x in issue["customFields"] if x["name"] == "Type"][0]
        issue["Type"] = type_field["value"]["name"]
        return issue

    def get_comments(self, issue_id):
        params = {"fields": "$type,id,text"}
        return self._client.get(f"issues/{issue_id}/comments", params=params).json()

    def update_deployed_field(self, issue_id):
        payload = {
            "customFields": [
                {
                    "name": "Deployed",
                    "$type": "SimpleIssueCustomField",
                    "value": time.time() * 1000,
                }
            ]
        }
        self._client.post(f"issues/{issue_id}", json=payload)

    def validate_issue(self, issue_id):
        try:
            if self.get_issue(issue_id):
                return True
        except Exception:
            pass
        return False

    def comment(self, issue_id, comment):
        payload = {"text": comment}
        self._client.post(f"issues/{issue_id}/comments", json=payload)

    def update_state(self, issue_id, status):
        payload = {
            "customFields": [
                {
                    "name": "State",
                    "$type": "StateIssueCustomField",
                    "value": {"name": status},
                }
            ]
        }
        self._client.post(f"issues/{issue_id}", json=payload)

    def add_tag(self, issue_id, label):
        params = {"fields": "id,name", "query": label}
        tag = self._client.get("issueTags", params=params).json()

        params = {"fields": "$type,id,tags($type,id,name)"}
        issue = self._client.get(f"issues/{issue_id}", params=params).json()

        issue["tags"].append(tag[0])

        payload = {"tags": issue["tags"]}
        self._client.post(f"issues/{issue_id}", json=payload)

    def assign_to(self, issue_id, user):
        payload = {
            "customFields": [
                {
                    "name": "Assignee",
                    "$type": "SingleUserIssueCustomField",
                    "value": {"login": user},
                }
            ]
        }
        self._client.post(f"issues/{issue_id}", json=payload)

    def get_link(self, issue_id):
        return f"{self._issue_url}{issue_id}"

    def get_issue_ids(self, commits):
        issue_ids = []
        for c in commits:
            issue_id = self.get_card_from_name(c.commit.message)
            if issue_id:
                issue_ids.append(issue_id)
        return issue_ids

    def get_card_from_name(self, name):
        if re.search(REGEX, name):
            id_card = re.findall(REGEX, name)[0]
            if self.validate_issue(id_card):
                return id_card
        return None

    def get_ids_from_release_body(self, body):
        return list(set(re.findall(REGEX, body)))

    def replace_card_names_with_md_links(self, text):
        return re.sub(REGEX, f"[\\1]({self._issue_url}\\1)", text)
