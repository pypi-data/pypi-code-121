import codecs
import json
import os
from datetime import datetime
from typing import List, Union, Set, Dict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from ruamel.yaml import YAML

from teko.helpers.clog import CLog
from teko.helpers.exceptions import TekoJiraException, raise_jira_exception
from teko.models.jira_tool.jira_testcase import JiraTestData


def quoted_testcase_name(name: str):
    name = name.replace("'", "\\'")
    return name


class JiraService:
    """
    Jira API docs: https://support.smartbear.com/zephyr-scale-server/api-docs/v1/
    """

    def __init__(self, config={}):
        """

        :param config: a dict like this, if something is missing, it will get from env variable
                {
                    "server": "https://jira.teko.vn",
                    "jira_username": "jira_username",
                    "jira_password": "jira_password",
                    "confluence_username": "confluence_username",
                    "confluence_password": "confluence_password",
                    "project_key": "PRJ",
                }
        """

        self.success = None

        load_dotenv()
        self.project_key = config.get('project_key') or os.getenv('JIRA_PROJECT_KEY')
        server = config.get('server') or os.getenv('JIRA_SERVER')
        jira_username = config.get('jira_username') or os.getenv('JIRA_USERNAME')
        jira_password = config.get('jira_password') or os.getenv('JIRA_PASSWORD')
        confluence_username = config.get('confluence_username') or os.getenv('CONFLUENCE_USERNAME')
        confluence_password = config.get('confluence_password') or os.getenv('CONFLUENCE_PASSWORD')

        if not self.project_key or not server or not jira_username or not jira_password or not confluence_username or not confluence_password:
            raise_jira_exception("No valid JIRA configuration found, please set JIRA_SERVER, JIRA_PROJECT_KEY, "
                                 "JIRA_USERNAME, JIRA_PASSWORD, CONFLUENCE_USERNAME and CONFLUENCE_PASSWORD "
                                 "environment variables first.")

        if not server.startswith("http://") and not server.startswith("https://"):
            server = "https://" + server
        self.base_api_url = urljoin(server, 'rest/atm/1.0/')
        self.base_api_tests_url = urljoin(server, 'rest/tests/1.0/')
        self.base_api_2_url = urljoin(server, 'rest/api/2/')

        self.jira_session = requests.session()
        self.jira_session.auth = (jira_username, jira_password)

        self.confluence_session = requests.session()
        self.confluence_session.auth = (confluence_username, confluence_password)

    def search_testcase(self, name) -> Union[JiraTestData, None]:
        query = f'projectKey = "{self.project_key}"'
        if name:
            query += f' AND name = "{quoted_testcase_name(name)}"'

        params = {
            "query": query
        }

        url = urljoin(self.base_api_url, "testcase/search")

        res = self.jira_session.get(url=url, params=params)

        if res.status_code != 200:
            CLog.error(f"Failed to search for test case \"{name}\".")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(f"Forbidden: You don't have permission to send request GET to {url} with params {params}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}: {res.text}.")
            return None

        raw = res.text

        testcases_json = json.loads(raw)

        return JiraTestData().from_dict(testcases_json[0]) if testcases_json else None

    def delete_trace_link(self, link_id):
        url = urljoin(self.base_api_url, f"tracelink/{link_id}")

        res = self.jira_session.delete(url=url)

        if res.status_code != 200:
            CLog.error(f"Failed to delete trace link {link_id}.")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(f"Forbidden: You don't have permission to send request DELETE to {url}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}: {res.text}.")
            return

        raw = res.text

        testcases_json = json.loads(raw)

        CLog.info(f"{json.dumps(testcases_json)}")

    def empty_trace_links(self, test_id):
        url_confluence = urljoin(self.base_api_tests_url, f"testcase/{test_id}/tracelinks/confluencepage")

        res = self.jira_session.get(url=url_confluence)

        if res.status_code != 200:
            CLog.error(f"Failed to clear confluence links of test case \"{test_id}\".")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(f"Forbidden: You don't have permission to send request GET to {url_confluence}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}. View detail at: {res.url}.")
        else:
            raw = res.text
            links = json.loads(raw)
            for link in links:
                self.delete_trace_link(link["id"])

        url_web = urljoin(self.base_api_tests_url, f"testcase/{test_id}/tracelinks/weblink")

        res = self.jira_session.get(url=url_web)

        if res.status_code != 200:
            CLog.error(f"Failed to clear web links of test case \"{test_id}\".")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(f"Forbidden: You don't have permission to send request GET to {url_web}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}. View detail at: {res.url}.")
        else:
            raw = res.text
            links = json.loads(raw)
            for link in links:
                self.delete_trace_link(link["id"])

    def add_confluence_links(self, test_id, confluences: List[str]):
        url = urljoin(self.base_api_tests_url, "tracelink/bulk/create")

        if not confluences:
            return

        confluences_data = []

        for confluence_url in confluences:
            res = self.confluence_session.get(url=confluence_url)
            if res.status_code != 200:
                CLog.error(f"Failed to get the id of confluence page {confluence_url}.")
                if res.status_code == 401:
                    CLog.error(f"Unauthorized: Authenticated failed.")
                elif res.status_code == 403:
                    CLog.error(f"Forbidden: You don't have permission to send request GET to {confluence_url}.")
                elif not res.text:
                    CLog.error(f"HTTP Error {res.status_code}. No response message.")
                else:
                    CLog.error(f"HTTP Error {res.status_code}. View detail at: {res.url}.")
                self.success = False
                return

            html = res.text
            soup = BeautifulSoup(html, "html.parser")
            page_id = soup.find("meta", {"name": "ajs-page-id"})["content"]

            confluences_data.append({
                "testCaseId": test_id,
                "confluencePageId": page_id,
                "typeId": 1
            })

        res = self.jira_session.post(url=url, json=confluences_data)

        if res.status_code != 200:
            CLog.error(f"Failed to add confluence links for test case \"{test_id}\".")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(
                    f"Forbidden: You don't have permission to send request POST to {url} with payload {confluences_data}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}: {res.text}.")
            self.success = False

    def add_web_links(self, test_id, webs: List[Union[str, dict]]):
        url = urljoin(self.base_api_tests_url, "tracelink/bulk/create")

        if not webs:
            return

        webs_data = []

        for web in webs:
            if isinstance(web, str):
                webs_data.append({
                    "url": web,
                    "urlDescription": web,
                    "testCaseId": test_id,
                    "typeId": 1
                })
            else:
                webs_data.append({
                    "url": web.get('url'),
                    "urlDescription": web.get('description'),
                    "testCaseId": test_id,
                    "typeId": 1
                })

        res = self.jira_session.post(url=url, json=webs_data)

        if res.status_code != 200:
            CLog.error(f"Failed to add web links for test case \"{test_id}\".")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(
                    f"Forbidden: You don't have permission to send request POST to {url} with payload {webs_data}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}: {res.text}.")
            self.success = False

    def add_links(self, test_id, confluences: List[str], webs: List[dict]):
        self.empty_trace_links(test_id)

        self.add_confluence_links(test_id, confluences)

        self.add_web_links(test_id, webs)

    def create_folder(self, name: str, type: str):
        data = {
            "projectKey": self.project_key,
            "name": name,
            "type": type
        }

        url = urljoin(self.base_api_url, "folder")

        """
        Ignore failure
        """
        res = self.jira_session.post(url=url, json=data)
        if res.status_code == 401:
            CLog.error(f"Cannot create {type} folder {name}.")
            CLog.error(f"Unauthorized: Authenticated failed.")
        if res.status_code == 403:
            CLog.error(f"Cannot create {type} folder {name}.")
            CLog.error(f"Forbidden: You don't have permission to send request POST to {url} with payload {data}.")
        if res.status_code != 201:
            CLog.info(f"{type} folder {name} has already exists.")

    def get_test_id(self, test_key) -> Union[int, None]:
        url = urljoin(self.base_api_tests_url, f"testcase/{test_key}")

        res = self.jira_session.get(url=url, params={"fields": "id"})
        if res.status_code != 200:
            CLog.error(f"Failed to get the id of test case {test_key}.")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(f"Forbidden: You don't have permission to send request GET to {url}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}. View detail at: {res.url}.")
            self.success = False
            return

        raw = res.text
        return json.loads(raw).get('id')

    def get_cycle_id(self, cycle_key) -> Union[int, None]:
        url = urljoin(self.base_api_tests_url, f"testrun/{cycle_key}")

        res = self.jira_session.get(url=url, params={"fields": "id"})
        if res.status_code != 200:
            CLog.error(f"Failed to get the id of test case {cycle_key}.")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(f"Forbidden: You don't have permission to send request GET to {url}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}. View detail at: {res.url}.")
            self.success = False
            return

        raw = res.text
        return json.loads(raw).get('id')

    def get_issue_id(self, issue_key) -> Union[str, None]:
        url = urljoin(self.base_api_2_url, f"issue/{issue_key}")
        res = self.jira_session.get(url=url, params={"fields": "id"})
        if res.status_code != 200:
            CLog.error(f"Failed to get the id of issue {issue_key}.")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(f"Forbidden: You don't have permission to send request GET to {url}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}. View detail at: {res.url}.")
            self.success = False
            return

        raw = res.text
        return json.loads(raw).get('id')

    def add_cycle_to_issues(self, cycle_key: str, issue_keys: Set[str], issue_ids: Dict):
        url = urljoin(self.base_api_tests_url, "tracelink/issue/testrun/bulk/create")

        cycle_id = self.get_cycle_id(cycle_key)

        data = [
            {
                "issueId": issue_ids[issue_key],
                "testRunId": cycle_id,
                "typeId": 2
            } for issue_key in issue_keys
        ]

        res = self.jira_session.post(url=url, json=data)
        if res.status_code != 200:
            CLog.error(f"Failed to get add cycle {cycle_key} into issue {', '.join(sorted(issue_keys))}.")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(f"Forbidden: You don't have permission to send request GET to {url}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}. View detail at: {res.url}.")
            self.success = False
            return

        CLog.info(f"Added cycle {cycle_key} into issue {', '.join(issue_keys)} successfully.")

    def prepare_testcase_data(self, testcase: JiraTestData) -> dict:
        if not testcase.projectKey:
            testcase.projectKey = self.project_key

        data = {
            'name': testcase.name,
            'projectKey': testcase.projectKey,
            'folder': testcase.folder,
            'objective': testcase.objective,
            'precondition': testcase.precondition,
            'status': testcase.status,
            'labels': testcase.labels
        }

        data.pop("status")

        if testcase.testScript:
            testscript = testcase.testScript.to_dict()
            testscript.pop("id")
            if testscript["type"] == "PLAIN_TEXT":
                testscript.pop("steps")
            elif testscript["type"] == "STEP_BY_STEP":
                testscript.pop("text")
            data.update({'testScript': testscript})

        if testcase.folder == "":
            data.pop("folder")

        if testcase.issueLinks:
            data['issueLinks'] = testcase.issueLinks

        return data

    def create_testcase(self, testcase: JiraTestData) -> Union[str, None]:
        data = self.prepare_testcase_data(testcase)
        url = urljoin(self.base_api_url, "testcase")
        res = self.jira_session.post(url=url, json=data)

        if res.status_code != 201:
            CLog.error(f"Failed to create test case \"{testcase.name}\".")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(f"Forbidden: You don't have permission to send request POST to {url} with payload {data}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}: {res.text}.")
            self.success = False
            return

        raw = res.text

        testcase_json = json.loads(raw)
        key = testcase_json['key']
        CLog.info(f"Created test \"{testcase.name}\" successfully. Test key: {key}.")
        return key

    def update_testcase(self, key: str, testcase: JiraTestData) -> Union[str, None]:
        url = urljoin(self.base_api_url, f"testcase/{key}")
        data = self.prepare_testcase_data(testcase)
        data.pop('projectKey')
        res = self.jira_session.put(url=url, json=data)

        if res.status_code != 200:
            CLog.error(f"Failed to update test case \"{testcase.name}\".")
            if res.status_code == 401:
                CLog.error(f"Unauthorized: Authenticated failed.")
            elif res.status_code == 403:
                CLog.error(f"Forbidden: You don't have permission to send request PUT to {url} with payload {data}.")
            elif not res.text:
                CLog.error(f"HTTP Error {res.status_code}. No response message.")
            else:
                CLog.error(f"HTTP Error {res.status_code}: {res.text}.")
            self.success = False
            return

        CLog.info(f"Updated test \"{testcase.name}\" successfully. Test key: {key}.")
        return key

    def create_or_update_testcases_by_name(self, testcases: List[JiraTestData]) -> List[JiraTestData]:
        CLog.info("Creating/Updating test cases.")
        self.success = True

        folders = set()

        for testcase in testcases:
            if testcase.folder:
                folders.add(testcase.folder)

        for folder in folders:
            self.create_folder(folder, "TEST_CASE")

        for testcase in testcases:
            existing_testcase = self.search_testcase(name=testcase.name)
            if not existing_testcase:
                key = self.create_testcase(testcase)
                testcase.key = key
            else:
                key = self.update_testcase(existing_testcase.key, testcase)
                testcase.key = key
            if key:
                self.add_links(
                    test_id=self.get_test_id(key),
                    confluences=testcase.confluenceLinks,
                    webs=testcase.webLinks
                )

        if not self.success:
            raise_jira_exception("Creating/updating test cases process did not succeed.")

        return testcases

    def prepare_testrun_data(self, testcase: JiraTestData) -> dict:
        if not testcase.projectKey:
            testcase.projectKey = self.project_key

        data = {
            'testCaseKey': testcase.key,
            'status': testcase.testrun_status,
            'environment': testcase.testrun_environment,
            'executionTime': testcase.testrun_duration,
            'executionDate': testcase.testrun_date,
        }

        return data

    def create_test_cycles(self, testcases: List[JiraTestData]):
        CLog.info("Creating test cycles.")
        self.success = True

        cycles_by_folder = dict()

        issue_ids = dict()

        issues_by_folder = dict()

        for testcase in testcases:
            existing_testcase = self.search_testcase(name=testcase.name)
            if not existing_testcase:
                CLog.error(f"Testcase with name \"{testcase.name}\" not existed.")
                self.success = False
            else:
                testcase.key = existing_testcase.key
                CLog.info(f"Testcase with name \"{testcase.name}\" existed.")
                folder = testcase.testrun_folder
                if cycles_by_folder.get(folder) is None:
                    cycles_by_folder[folder] = []
                if issues_by_folder.get(folder) is None:
                    issues_by_folder[folder] = set()

                cycles_by_folder[folder].append(self.prepare_testrun_data(testcase))
                for issue_key in existing_testcase.issueLinks:
                    if not issue_ids.get(issue_key):
                        issue_ids[issue_key] = self.get_issue_id(issue_key)
                    issues_by_folder[folder].add(issue_key)

        if not self.success:
            raise_jira_exception("Creating test cycle process did not succeed.")

        url = urljoin(self.base_api_url, "testrun")

        for folder in cycles_by_folder.keys():
            self.create_folder(folder, "TEST_RUN")

        for folder, cycles in cycles_by_folder.items():
            data = {
                "projectKey": self.project_key,
                "name": f"[{self.project_key}] Cycle {datetime.now()}",
                "folder": folder,
                "items": cycles
            }

            if not folder:
                data.pop("folder")

            res = self.jira_session.post(url=url, json=data)

            if res.status_code != 201:
                CLog.error(f"Failed to create test cycle.")
                if res.status_code == 401:
                    CLog.error(f"Unauthorized: Authenticated failed.")
                elif res.status_code == 403:
                    CLog.error(
                        f"Forbidden: You don't have permission to send request POST to {url} with payload {data}.")
                elif not res.text:
                    CLog.error(f"HTTP Error {res.status_code}. No response message.")
                else:
                    CLog.error(f"HTTP Error {res.status_code}: {res.text}.")
                self.success = False
                return

            raw = res.text

            testcycle_json = json.loads(raw)
            key = testcycle_json['key']
            if folder:
                CLog.info(f"Test cycle {key} created in folder {folder}.")
            else:
                CLog.info(f"Test cycle {key} created.")

            self.add_cycle_to_issues(key, issues_by_folder[folder], issue_ids)

        if not self.success:
            raise_jira_exception("Creating test cycles process does not succeeded.")

    @staticmethod
    def read_test_from_file(testcase_file):
        """

        :param testcase_file: yaml or json file
        :return:
        """
        filename, ext = os.path.splitext(testcase_file)
        CLog.info(f"Reading {os.path.abspath(testcase_file)}.")
        if ext == ".json":
            with codecs.open(testcase_file, "r", encoding="utf-8") as f:
                try:
                    testcase_data = json.load(f)
                except Exception:
                    raise_jira_exception("Invalid json format.")

        elif ext == ".yaml":
            with codecs.open(testcase_file, "r", encoding="utf-8") as f:
                yaml = YAML(typ="safe")
                try:
                    testcase_data = yaml.load(f)
                except Exception:
                    raise_jira_exception("Invalid yaml format.")
        else:
            raise_jira_exception(f"File format not supported: {ext}.")

        testcases = []
        for t in testcase_data:
            name = t.get('name')
            if not name:
                raise_jira_exception("A test case is missing its name.")
            if name.count('\\') or name.count('"'):
                raise_jira_exception("Invalid character(s) in the testcase name. Avoid using '\\' and '\"'.")
            if t.get('folder') and t['folder'][0] != '/':
                t['folder'] = '/' + t['folder']
            if t.get('testrun_folder') and t['testrun_folder'][0] != '/':
                t['testrun_folder'] = '/' + t['testrun_folder']
            try:
                testcases.append(JiraTestData().from_dict(t))
            except Exception:
                raise_jira_exception(f"Failed to parse test data from file {testcase_file}.")

        return testcases

    @staticmethod
    def write_test_to_file(testcase_file, testcases):
        """

        :param testcase_file: yaml or json file
        :return:
        """
        testcases_json = []
        for t in testcases:
            CLog.info(f"{t}")
            data = t.to_dict()
            testcases_json.append(data)

        filename, ext = os.path.splitext(testcase_file)
        CLog.info(f"Writing {os.path.abspath(testcase_file)}.")
        if ext == ".json":
            with codecs.open(testcase_file, "w", encoding="utf-8") as f:
                json.dump(testcases_json, f, indent=2)
        elif ext == ".yaml":
            with codecs.open(testcase_file, "w", encoding="utf-8") as f:
                yaml = YAML(typ="safe")
                yaml.indent(offset=2)
                yaml.dump(testcases_json, f)
        else:
            raise TekoJiraException(f"File format not supported: {ext}.")


if __name__ == "__main__":
    jira_srv = JiraService()

    testcase_file = "../../../sample/testcases.yaml"
    testcases = JiraService.read_test_from_file(testcase_file)
    jira_srv.create_or_update_testcases_by_name(testcases)

    testcycle_file = "../../../sample/testcycles.yaml"
    testcases = JiraService.read_test_from_file(testcycle_file)
    jira_srv.create_test_cycles(testcases)
