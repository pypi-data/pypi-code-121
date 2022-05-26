from copy import deepcopy as copy
from re import sub
class FlagRemediationMessages():
    def __init__(self, project_name):
        self.starting_string = f"\nProject {project_name} has been flagged due to "
        self.cannot_guarantee_string = "\nWe cannot guarantee this project will automatically be migrated."
        self.project_messages = []
    
    def generate_report_entry(self):
        report_string = f"{self.starting_string}"
        remediation_string = f"{self.cannot_guarantee_string} We recommend the following next steps:"
        for item in self.project_messages:
            next_steps = sub(' {2,}', '\t  ', item['next_steps'].strip())
            report_string += f"\n\t- {item['message']}"
            remediation_string += f"\n\t- {next_steps}"
        return f"\n---{report_string}{remediation_string}\n---"
        
    def add_flag_message(self, asset, flag_condition):
        self.project_messages.append(self.get_flag_message(asset, flag_condition))

    def get_flag_message(self, asset, flag_condition):
        flag_condition = str(flag_condition)
        flag_remediation = {
            "repo_size": {
                "message": f"repo size exceeding {flag_condition}",
                "next_steps": "clean up repository using these tips: https://docs.gitlab.com/ee/user/project/repository/reducing_the_repo_size_using_git.html"
            },
            "storage_size": {
                "message": f"storage size exceeding {flag_condition}",
                "next_steps": """
                    Clean up repository using these tips: https://docs.gitlab.com/ee/user/project/repository/reducing_the_repo_size_using_git.html.
                    Examine any job artifacts that may be present in the project. Job artifacts do not migrate, but will contribute to the overall storage size of the project
                """
            },
            "issues": {
                "message": f"issue count exceeding {flag_condition}",
                "next_steps": """
                    Review the existing issues in the project to see if any can be deleted.
                    Unfortunately given the large number of issues, this project has a higher chance of failing compared to other projects with a lower issue count.
                    The only way to improve the chance of a successful import in this case is to decrease the number of issues in the project.
                """
            },
            "pipelines": {
                "message": f"number of executed pipelines exceeding {flag_condition}",
                "next_steps": "Trim or remove older CI pipelines using these steps: https://gitlab.com/gitlab-org/professional-services-automation/tools/migration/congregate/-/blob/master/runbooks/migrations-to-dot-com.md#trim-or-remove-project-ci-pipelines"
            },
            "merge_requests": {
                "message": f"number of merge requests exceeding {flag_condition}",
                "next_steps": """
                    Review the existing merge requests in the project to see if any can be deleted.
                    Unfortunately given the large number of merge requests, this project has a higher chance of failing compared to other projects with a lower merge request count.
                    We can try importing the project through the rails console instead of the API to improve the chances of a successful import, 
                    but this will require terminal level access to your destination GitLab instance and we still cannot guarantee this will be successful.
                """
            },
            "branches": {
                "message": f"number of branches exceeding {flag_condition}",
                "next_steps": "Remove any stale or merged branches"
            },
            "tags": {
                "message": f"number of tags exceeding {flag_condition}",
                "next_steps": """
                    Review repository for any tags that can be removed.
                    Before a migration starts, plan to remove all the tags in the remote repository.
                    Keep all of the tags in a local, up-to-date copy of the repository so you can push the tags back up to the remote after the migration completes
                """
            },
            "packages": {
                "message": f"built packages were detected: [{flag_condition}]",
                "next_steps": "Plan for a manual migration of this project's packages"
            },
            "container_registries": {
                "message": f"container registry size exceeded {flag_condition}",
                "next_steps": "Clean up any unused container registry repositories, images, and tags"
            }
        }
        return copy(flag_remediation.get(asset))