# -*- coding: utf-8 -*-

import copy
import datetime
import json
import re
import sys

from dateutil import tz
from rich.console import Console
from rich.table import Table

from suite_py.lib import logger
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.qainit_handler import QainitHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler
from suite_py.lib.handler.drone_handler import DroneHandler
from suite_py.commands.login import Login


class QA:
    def __init__(self, action, project, config, tokens, flags=None):
        self._action = action
        self._project = project
        self._flags = flags
        self._config = config
        self._tokens = tokens
        self._git = GitHandler(project, config)
        self._qainit = QainitHandler(project, config, tokens)
        self._youtrack = YoutrackHandler(config, tokens)
        self._drone = DroneHandler(config, tokens)

    def run(self):
        if not self._qainit.user_info():
            logger.warning("You're not logged in.")
            Login(self._config).run()

        if self._action == "list":
            self._list()
        elif self._action == "create":
            self._create()
        elif self._action == "update":
            self._update()
        elif self._action == "delete":
            self._delete()
        elif self._action == "freeze":
            self._freeze()
        elif self._action == "unfreeze":
            self._unfreeze()
        elif self._action == "check":
            self._check()
        elif self._action == "describe":
            self._describe()
        elif self._action == "update-quota":
            self._update_quota()
        elif self._action == "toggle-maintenance":
            self._toggle_maintenance()

    def _check(self):
        logger.info(
            "Checking configuration. If there is an issue, check ~/.suite_py/config.yml file and execute: suite-py login"
        )

        self._qainit.user_info()

    def _clean_date(self, datetime_str):
        # expected format: '2021-07-23T14:04:12.000000Z'
        datetime_object = datetime.datetime.strptime(
            datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        # Define time zones:
        utc_time_zone = tz.tzutc()
        local_time_zone = tz.tzlocal()
        # Convert time zone
        utc_datetime_object = datetime_object.replace(tzinfo=utc_time_zone)
        local_datetime_object = utc_datetime_object.astimezone(local_time_zone)
        return local_datetime_object.strftime("%d/%m/%Y %H:%M:%S %z")

    def _create_instance_table(self):
        instance_table = Table()
        instance_table.add_column("Name", style="purple")
        instance_table.add_column("Hash", style="green", width=32)
        instance_table.add_column("Card", style="white")
        instance_table.add_column("Created by", style="white")
        instance_table.add_column("Updated by", style="white")
        instance_table.add_column("Deleted by", style="white")
        instance_table.add_column("Last update", style="white")
        instance_table.add_column("Status", style="white")

        return instance_table

    def _insert_instance_record(self, table, qa):
        table.add_row(
            qa["name"],
            qa["hash"],
            qa["card"],
            qa.get("created", {}).get("github_username", "/")
            if qa["created"] is not None
            else "/",
            qa.get("updated", {}).get("github_username", "/")
            if qa["updated"] is not None
            else "/",
            qa.get("deleted", {}).get("github_username", "/")
            if qa["deleted"] is not None
            else "/",
            self._clean_date(qa["updated_at"]),
            qa["status"],
        )

    def _list(self):
        # init empty table with column (useful for reset)
        empty_table = self._create_instance_table()
        table = copy.deepcopy(empty_table)
        console = Console()

        # execute query with pagination and filtering
        page_number = 1
        while True:
            r = self._qainit.list(
                self._flags,
                page=page_number,
                page_size=self._config.qainit["table_size"],
            )
            response = r.json()
            qa_list = response["list"]
            for qa in qa_list:
                self._insert_instance_record(table, qa)

            console.print(table)

            # break conditions
            if response["page_number"] >= response["total_pages"]:
                break
            if not prompt_utils.ask_confirm(
                f"I found {response['total_entries']} results. Do you want to load a few more?",
                False,
            ):
                break
            page_number += 1
            # table reset
            table = copy.deepcopy(empty_table)

    def _describe(self):
        qa_hash = self._flags["hash"]
        jsonify = self._flags["json"]

        r = self._qainit.describe(qa_hash)

        issues = self._check_instance_issues(r)
        if issues:
            msg = "an issue" if len(issues) == 1 else f"{len(issues)} issues"
            logger.warning(f"⚠️  suite-py diagnostic tool found {msg}:")
            for i in issues:
                logger.warning(i)
            logger.warning(
                "If the problem persist write a detailed message on #team-devops"
            )
            sys.exit(-1)

        if jsonify:
            print(json.dumps(r, sort_keys=True, indent=2))
        else:
            # RESOURCES TABLE
            table = Table()
            table.add_column("Microservice", style="purple", no_wrap=True)
            table.add_column("Drone build")
            table.add_column("Branch", style="white")
            table.add_column("Last update", style="white")
            table.add_column("Status", style="white")

            # INSTANCE TABLE
            instance_table = self._create_instance_table()

            self._insert_instance_record(instance_table, r["list"])

            # DNS TABLE
            dns_table = Table()
            dns_table.add_column("Name", style="purple", no_wrap=True)
            dns_table.add_column("Record", style="green")

            console = Console()

            try:
                resources_list = sorted(r["list"]["resources"], key=lambda k: k["name"])
                for resource in resources_list:
                    if (
                        (
                            resource["type"] == "microservice"
                            or "service" in resource["name"]
                        )
                        and "dns" in resource
                        and resource["dns"] is not None
                    ):
                        for key, value in resource["dns"].items():
                            dns_table.add_row(key, value)
                    if resource["type"] == "microservice":
                        drone_url = (
                            (
                                "[blue][u]"
                                + "https://drone-1.prima.it/primait/"
                                + resource["name"]
                                + "/"
                                + resource["promoted_build"]
                                + "[/u][/blue]"
                            )
                            if resource["promoted_build"]
                            else "Not available"
                        )
                        table.add_row(
                            resource["name"],
                            drone_url,
                            resource["ref"]
                            if resource["ref"] == "master"
                            else f"[green]{resource['ref']}[/green]",
                            self._clean_date(resource["updated_at"]),
                            resource["status"],
                        )

                console.print(instance_table)
                console.print(dns_table)
                console.print(table)
            except TypeError as e:
                logger.error(f"Unexpected response format: {e}")

    def _delete(self):
        qa_hashes = self._flags["hashes"]
        for qa_hash in qa_hashes:
            self._qainit.delete(qa_hash)

    def _freeze(self):
        self._qainit.freeze(self._flags["hash"])

    def _unfreeze(self):
        self._qainit.unfreeze(self._flags["hash"])

    def _create(self):
        user = self._qainit.user_info()

        if not user["quota"]["remaining"] > 0:
            logger.error("There's no remaining quota for you.")
            sys.exit("-1")

        if "staging" in self._qainit.url:
            qa_default_name = (
                f"staging_{git.get_username()}_{self._git.current_branch_name()}"
            )
        else:
            qa_default_name = f"{git.get_username()}_{self._git.current_branch_name()}"

        qa_name = prompt_utils.ask_questions_input(
            "Choose the QA name: ", default_text=qa_default_name
        )

        card_match = re.match(r"[^\/]*_(?P<name>[A-Z]+-\d+)\/", qa_name)
        default_card_name = (
            card_match["name"] if card_match else self._config.user["default_slug"]
        )

        qa_card = prompt_utils.ask_questions_input(
            "Youtrack issue ID: ", default_text=default_card_name
        )

        if qa_card != "":
            try:
                self._youtrack.get_issue(qa_card)
            except Exception:
                logger.error("invalid Youtrack issue ID")
                sys.exit(-1)

        self._qainit.create(qa_name, qa_card, self._flags["services"])

    def _update(self):
        self._qainit.update(self._flags["hash"], self._flags["services"])

    def _update_quota(self):
        username = prompt_utils.ask_questions_input("Insert GitHub username: ")
        quota = prompt_utils.ask_questions_input("Insert new quota value: ")

        self._qainit.update_user_quota(username, quota)

    def _toggle_maintenance(self):
        self._qainit.maintenance()

    def _check_instance_issues(self, response):
        issues = []

        if not response["list"]:
            issues.append("QA not found")

        # Check if instance status is still pending
        if response["list"] and response["list"]["status"] in ["creating", "updating"]:
            # 1. Microservices list is empty?
            if len(response["list"]["resources"]) == 0:
                issues.append("Microservices list is empty, please be patient.")

            # 2. Check every resource
            stale_resources = self._filter_list(
                "status", ["creating", "updating"], response["list"]["resources"]
            )
            for resource in stale_resources:
                issues += self._check_resource_issues(resource)

            # 3. Check is instance is stuck in a stale status
            if len(stale_resources) == 0:
                logger.warning("Trying to call qainit to force QA update...")
                self._qainit.force_update(response["list"]["hash"])
                issues.append(
                    "Your QA was in a stale status and has been fixed, launch `suite-py describe` again please."
                )

        return issues

    def _check_resource_issues(self, resource):
        issues = []

        build = self._drone.get_repo_build(resource["name"], resource["promoted_build"])

        if "stages" not in build:
            issues.append("Suite-py is unable to locate drone build.")
            return issues

        qainit_step = self._filter_list("name", ["qainit-it"], build["stages"])[0]
        # Check if build is succeded
        if build["status"] == "success" or qainit_step["status"] == "error":
            issues.append(
                f"Something between Drone and Qainit went wrong, did you try to restart the build? {self._drone.get_repo_build_url(resource['name'], resource['promoted_build'])}"
            )

        # Check if build is killed
        elif build["status"] == "killed":
            issues.append(
                f"Seems someone killed the build, did you try to restart the build? {self._drone.get_repo_build_url(resource['name'], resource['promoted_build'])}"
            )

        # Check if build is failed
        elif build["status"] == "failure":
            build_pipeline = self._filter_list("name", ["build_qa"], build["stages"])[0]
            if build_pipeline and build_pipeline["status"] == "failed":
                issues.append(
                    f"Something went wrong during microservice build step, check the logs {self._drone.get_build_and_pipeline_url(resource['name'], resource['promoted_build'], build_pipeline['number'])}"
                )

            deploy_pipeline = self._filter_list(
                "name", ["deploy-it-qa"], build["stages"]
            )[0]
            if deploy_pipeline and deploy_pipeline["status"] == "failed":
                issues.append(
                    f"Something went wront during microservice deploy step, check the logs {self._drone.get_build_and_pipeline_url(resource['name'], resource['promoted_build'], deploy_pipeline['number'])}"
                )
        # Check if build is running for over an hour
        elif (
            build["status"] == "running"
            and self._difference_in_hours(build["started"]) >= 1
        ):
            issues.append(
                f"It looks like the build is stuck, did you try to restart the build? {self._drone.get_repo_build_url(resource['name'], resource['promoted_build'])}"
            )

        return issues

    def _filter_list(self, search_key, in_list, search_list):
        return list(filter(lambda l: l[search_key] in in_list, search_list))

    def _difference_in_hours(self, unix_timestamp):
        ts = datetime.datetime.fromtimestamp(unix_timestamp)
        current_ts = datetime.datetime.utcnow()

        return (current_ts - ts).total_seconds() / 60 / 60
