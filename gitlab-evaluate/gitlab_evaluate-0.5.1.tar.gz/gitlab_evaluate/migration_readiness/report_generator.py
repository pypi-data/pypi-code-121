from copy import deepcopy as copy
from traceback import print_exc
from gitlab_ps_utils.json_utils import json_pretty
from gitlab_ps_utils.api import GitLabApi
from gitlab_ps_utils.processes import MultiProcessing
from gitlab_evaluate.lib import utils, limits
from gitlab_evaluate.lib import api as api_helpers
from gitlab_evaluate.lib.flag_remediation import FlagRemediationMessages


class ReportGenerator():
    def __init__(self, host, token, filename=None, output_to_screen=False, api=None, processes=None):
        self.host = host
        self.token = token
        self.csv_file = 'evaluate_output.csv'
        self.rollup_file = 'flags_evaluate_output.csv'
        self.output_to_screen = output_to_screen
        self.gitlab_api = api if api else GitLabApi()
        self.multi = MultiProcessing()
        self.processes = processes
        if filename:
            self.set_filenames(filename)
        self.csv_columns = [
            'Project',
            'ID',
            'kind',
            'archived',
            'Pipelines',
            'Pipelines_over',
            'Issues',
            'Issues_over',
            'Branches',
            'Branches_over',
            'commit_count',
            'commit_count_over',
            'Merge Requests',
            'Merge Requests_over',
            'storage_size',
            'storage_size_over',
            'repository_size',
            'repository_size_over',
            'Tags',
            'Tags_over',
            'Package Types In Use',
            'Total Packages Size',
            'Container Registry Size']
        utils.write_to_csv(self.csv_file, self.csv_columns, [])
        utils.write_to_csv(self.rollup_file, self.csv_columns, [])
        with open("report.txt", "w") as f:
            f.write("Evaluate Report: ")
    
    def handle_getting_data(self):
        self.multi.start_multi_process_stream(self.get_all_project_data, self.gitlab_api.list_all(self.host, self.token, "/projects?statistics=true"), processes=self.processes)

    def get_all_project_data(self, p):
        results = {}
        pid = p.get('id')
        statistics = p.get('statistics')
        if self.output_to_screen:
            print('+' * 40)
            print(f"Name: {p.get('name')} ID: {pid}")
            print(f"Desc: {p.get('description')}")
            print(f"Archived: {p.get('archived')}")
        results["Project"] = p.get('name')
        results["ID"] = pid
        results["archived"] = p.get('archived')
        headers={
            'PRIVATE-TOKEN': self.token
        }

        ## Get the full project info with stats
        messages = FlagRemediationMessages(p.get('name'))
        full_stats_url = api_helpers.proj_info_get(pid, self.host)
        api_helpers.check_full_stats(full_stats_url, p, results, headers=headers)

        try:
            flags = []
            pipelines_url = api_helpers.proj_pl_get(pid, self.host)
            flags.append(self.handle_check(
                messages,
                api_helpers.check_x_total_value_update_dict(
                    utils.check_num_pl, p, pipelines_url, headers, "Pipelines", "Pipelines_over", results),
                "pipelines",
                limits.PIPELINES_COUNT))
            
            ## Get number of issues per project
            issues_url = api_helpers.proj_issue_get(pid, self.host)
            flags.append(self.handle_check(
                messages,
                api_helpers.check_x_total_value_update_dict(
                    utils.check_num_issues, p, issues_url, headers, "Issues", "Issues_over", results),
                "issues",
                limits.ISSUES_COUNT))

            ## Get number of branches per project
            branches_url = api_helpers.proj_branch_get(pid, self.host)
            flags.append(self.handle_check(
                messages,
                api_helpers.check_x_total_value_update_dict(
                    utils.check_num_br, p, branches_url, headers, "Branches", "Branches_over", results),
                "branches",
                limits.BRANCHES_COUNT))

            ## Get number of merge requests per project
            mrequests_url = api_helpers.proj_mr_get(pid, self.host)
            flags.append(self.handle_check(
                messages,
                api_helpers.check_x_total_value_update_dict(
                    utils.check_num_mr, p, mrequests_url, headers, "Merge Requests", "Merge Requests_over", results),
                "merge_requests",
                limits.MERGE_REQUESTS_COUNT))

            ## Get number of tags per project
            tags_url = api_helpers.proj_tag_get(pid, self.host)
            flags.append(self.handle_check(
                messages,
                api_helpers.check_x_total_value_update_dict(
                    utils.check_num_tags, p, tags_url, headers, "Tags", "Tags_over", results),
                "tags",
                limits.TAGS_COUNT))

            ## Get list of package types
            packages_in_use = set([x.get('package_type', '') 
                for x in self.gitlab_api.list_all(self.host, self.token, api_helpers.proj_packages_url(pid))])
            results['Package Types In Use'] = ", ".join(packages_in_use) if packages_in_use else "N/A"
            if packages_in_use:
                flags.append(True)
                self.handle_check(messages, True, "packages", copy(results['Package Types In Use']))
            
            ## Get total packages size
            results['Total Packages Size'] = utils.sizeof_fmt(statistics.get('packages_size'))
            
            ## Get container registry size
            results['Container Registry Size'], flag_registries = api_helpers.get_registry_size(pid, self.host, self.token)
            self.handle_check(messages, flag_registries, 'container_registries', utils.sizeof_fmt(limits.CONTAINERS_SIZE))

            try:
                self.write_output_to_files(flags, messages, results)
            except Exception:
                print(print_exc())

        except Exception:
            print(print_exc())
    
    def handle_check(self, messages, flagged_asset, asset_type, flag_condition):
        if flagged_asset == True:
            messages.add_flag_message(asset_type, flag_condition)
        return flagged_asset

    def set_filenames(self, filename):
        self.csv_file = filename
        self.rollup_file = f"flags_{filename}"
    
    def write_output_to_files(self, flags, messages, results):
        dict_data = []
        dict_data.append({x: results.get(x) for x in self.csv_columns})
        utils.write_to_csv(self.csv_file, self.csv_columns, dict_data, append=True)

        if True in flags:
            utils.write_to_csv(self.rollup_file, self.csv_columns, dict_data, append=True)
            with open("report.txt", "a") as f:
                print("Writing to report")
                f.write(messages.generate_report_entry())
        if self.output_to_screen:
            print(f"""
            {'+' * 40}
            {json_pretty(results)}
            """)

    def write_line_to_file(self, message):
        print(message)
        with open("report.txt", "a") as f:
            f.write(f"\n{message}")
