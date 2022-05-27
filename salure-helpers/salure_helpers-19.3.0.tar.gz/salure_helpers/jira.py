import json

import pandas as pd
import requests


class Jira:
    def __init__(self, access_token: str, base_url: str = "https://salure.atlassian.net/"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Basic {access_token}",
            "Content-Type": "application/json"
        }

    def get_issues(self, jql_filter: str = None, get_extra_fields: list = None) -> pd.DataFrame:
        total_response = []
        got_all_results = False
        no_of_loops = 0
        while not got_all_results:
            query = {
                'startAt': f'{100 * no_of_loops}',
                'maxResults': '100',
                'fields': ["summary", "issuetype", "timetracking", "timespent", "description", "assignee", "project"],
                'fieldsByKeys': 'false'
            }
            if jql_filter is not None:
                query['jql'] = jql_filter
            if get_extra_fields is not None:
                query['fields'] += get_extra_fields
            response = requests.post(f"{self.base_url}rest/api/3/search", headers=self.headers, data=json.dumps(query))
            if response.status_code == 200:
                response_json = response.json()
                no_of_loops += 1
                got_all_results = False if len(response_json['issues']) == 100 else True
                total_response += response_json['issues']
            else:
                raise ConnectionError("Error getting issues from Jira")

        print(f"Received {len(total_response)} issues from Jira")

        df = pd.json_normalize(total_response)

        return df

    def get_projects(self) -> pd.DataFrame:
        total_response = []
        got_all_results = False
        no_of_loops = 0

        while not got_all_results:
            query = {
                'startAt': f'{50 * no_of_loops}',
                'maxResults': '50',
                'expand': 'description'
            }
            response = requests.get(f"{self.base_url}rest/api/3/project/search", headers=self.headers, params=query)

            if response.status_code == 200:
                response_json = response.json()
                no_of_loops += 1
                got_all_results = False if len(response_json['values']) == 50 else True
                total_response += response_json['values']
            else:
                raise ConnectionError("Error getting projects from Jira")

        print(f"Received {len(total_response)} projects from Jira")

        df = pd.json_normalize(total_response)

        return df
