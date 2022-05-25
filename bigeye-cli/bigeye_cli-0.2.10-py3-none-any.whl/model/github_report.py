import os
from dataclasses import dataclass

from github import Github
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Repository import Repository
from bigeye_sdk.generated.com.torodata.models.generated import ComparisonTableInfo
from bigeye_cli.model.vendor_report import VendorReport, _format_report, _format_group_report


@dataclass
class GitHubReport(VendorReport):
    github_token: str
    git: Github = None
    repo: Repository = None
    pr: PullRequest = None
    issue: Issue = None

    def __post_init__(self):
        self.git = Github(self.github_token)
        self.repo = self.git.get_repo(os.environ['CURRENT_REPO'])
        self.pr = self.repo.get_pull(int(os.environ['PR_NUMBER']))

    def publish(self, source_table_name: str, target_table_name: str, cti: ComparisonTableInfo) -> int:

        # NOTE: Do we want to add the ability to notify based on tolerance??
        if cti.alerting_metric_count != 0:
            report = _format_report(source_table_name, target_table_name, cti)
            failure_title = f'Bigeye Delta failure for PR: {self.pr.title}'
            self.issue = self.repo.create_issue(title=failure_title,
                                                body=report,
                                                assignee=self.pr.user,
                                                labels=['bug'])
            return 1
        elif cti.schema_match is False:
            question_title = f"Schema mismatch detected in delta. Is this expected?"
            header = "#### Please confirm that the schemas are not supposed to match before approving Pull Request."
            tables = f"Source Table: {source_table_name}\nTarget Table: {target_table_name}"
            body = f"{header}\n{tables}"

            self.repo.create_issue(title=question_title,
                                   body=body,
                                   labels=['question'])
            return 0
        else:
            return 0

    def publish_group_bys(self, source_table_name: str, target_table_name: str, cti: ComparisonTableInfo):

        report = _format_group_report(source_table_name, target_table_name, cti)
        self.issue.create_comment(report)

