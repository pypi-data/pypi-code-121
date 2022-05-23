from typing import List

from teko.models.jira_export_test.test_step import TestStep


class SubTest:
    test_name: str = ''
    objective: str = ''
    precondition: str = ''

    def __init__(self, test_name: str = None, objective: str = None, precondition: str = None, **kwargs):
        self.precondition = precondition
        self.test_name = test_name
        self.objective = objective

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        return {
            "test_name": self.test_name,
            "objective": self.objective,
            "precondition": self.precondition
        }


class TestCase:
    test_id: int = 0
    test_name: str = ''
    issue_links: List[str] = []
    objective: str = ''
    precondition: str = ''
    priority: str = 'Normal'
    folder: str = ''
    web_links: List[str] = []
    confluence_links: List[str] = []
    plan: str = ''
    scripts: List[TestStep] = []
    sub_tests: List[SubTest] = []

    def __init__(self, **kwargs):
        for (key, value) in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        test_case_dict = {
            'name': self.test_name,
            'issueLinks': self.issue_links,
            'objective': self.objective,
            'precondition': self.precondition,
            'priority': self.priority,
            'folder': self.folder,
            'webLinks': self.web_links,
            'confluenceLinks': self.confluence_links,
            'testScript': {}
        }
        if self.plan:
            test_case_dict.update({'testScript': {'type': 'PLAIN_TEXT', 'text': self.plan}})
        if self.scripts:
            scripts = [script.to_dict() for script in self.scripts]
            test_case_dict.update({'testScript': {'type': 'STEP_BY_STEP', 'steps': scripts}})
        return test_case_dict
