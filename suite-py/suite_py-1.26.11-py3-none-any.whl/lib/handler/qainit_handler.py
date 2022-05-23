# -*- encoding: utf-8 -*-
import json
import sys

import requests
from github.GithubException import UnknownObjectException
from halo import Halo

from suite_py.lib import logger
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.github_handler import GithubHandler


class QainitHandler:

    scope_mapping = {
        "admin": [
            "update:user-quota",
            "delete:others-qa",
            "create:qa",
            "delete:qa",
            "describe:qa",
            "describe:others-qa",
            "update:qa",
            "update:others-qa",
            "list:qa",
            "list:others-qa",
        ],
        "dev": [
            "create:qa",
            "delete:qa",
            "describe:qa",
            "describe:others-qa",
            "update:qa",
            "update:others-qa",
            "list:qa",
            "list:others-qa",
        ],
        "external": ["create:qa", "delete:qa", "describe:qa", "list:qa", "update:qa"],
    }

    def __init__(self, project, config, tokens):
        self._project = project
        self._token = tokens.drone
        self._config = config
        self.url = self._config.qainit["url"]
        self.auth0_tenant = self._config.auth0["tenant"]
        self.auth0_token = self._config.get_cache(f"{self.auth0_tenant}_auth0_token")
        self._github = GithubHandler(tokens)
        self._git = GitHandler(project, config)

        if "url" not in config.qainit:
            self.usage()
            sys.exit(-1)

    def usage(self):
        logger.warning(
            "Unable to use QA commands: missing qainit config in ~/.suite_py/config.yml"
        )
        logger.warning(
            "Update your config.yml as: https://github.com/primait/suite_py/blob/master/.config.yml.dist"
        )

    def user_info(self):
        r = self._execute("GET", "/api/v1/user")

        if r.status_code == 401:
            return None

        logger.debug(json.dumps(r.json(), indent=2))

        return r.json()

    def update_user_quota(self, username, quota):
        body = {"github_username": f"{username}", "quota": f"{quota}"}
        logger.debug(json.dumps(body))
        r = self._execute(
            "POST",
            "/api/v1/user/quota",
            body=json.dumps(body),
        )

        logger.info("Quota updated.")
        logger.debug(json.dumps(r.json(), indent=2))

    def create(self, name, card, services):
        srv_list = self.create_services_body(services)
        body = {"name": name, "card": card, "services": srv_list}

        logger.debug(json.dumps(body))
        r = self._execute(
            "POST",
            "/api/v1/qa",
            body=json.dumps(body),
        )

        logger.info(f"QA creation initiated. Your namespace hash: {r.json()['hash']}")
        logger.debug(json.dumps(r.json(), indent=2))

    def update(self, qa_hash, services):
        srv_list = self.create_services_body(services)

        body = {"services": srv_list}
        logger.debug(json.dumps(body))

        r = self._execute(
            "PUT",
            f"/api/v1/qa/{qa_hash}",
            body=json.dumps(body),
        )
        logger.info("QA update initiated")
        logger.debug(json.dumps(r.json(), indent=2))

    def list(self, params, page=1, page_size=10):
        filters = []
        status_values = '"created","creating","updated","updating","failed","frozen","freezing","unfreezing"'
        if len(params["status"]) > 0:
            status_values = ",".join([f'"{status}"' for status in params["status"]])
        filters.append(f"status=[{status_values}]")

        if params["user"] is not None:
            filters.append(f"user={params['user']}")

        if params["card"] is not None:
            filters.append(f"card={params['card']}")

        filters_string = "&".join(filters)

        return self._execute(
            "GET",
            f"/api/v1/qa?{filters_string}&page_size={page_size}&page={page}",
        )

    def delete(self, qa_hash):
        r = self._execute(
            "DELETE",
            f"/api/v1/qa/{qa_hash}",
        )
        logger.info(f"QA {qa_hash} deletion initiated")
        logger.debug(json.dumps(r.json(), indent=2))

    def describe(self, qa_hash):
        r = self._execute(
            "GET",
            f"/api/v1/qa/{qa_hash}",
        ).json()
        logger.debug(json.dumps(r, indent=2))

        return r

    def create_services_body(self, prj_list):
        srv_list = []
        ref = self._git.current_branch_name()
        for prj in prj_list:
            with Halo(text="Loading branches...", spinner="dots", color="magenta"):
                choices = [
                    {"name": branch.name, "value": branch.name}
                    for branch in self._github.get_branches(prj)
                ]
            if choices:
                choices.sort(key=lambda x: x["name"])
                ref = prompt_utils.ask_choices(
                    f"Select branch for project - {prj}: ", choices, default_text=ref
                )
            try:
                self._github.get_raw_content(prj, ref, ".service.yml")
            except UnknownObjectException:
                logger.error(
                    f".service.yml missing for project: {prj}, can't add microservice to QA"
                )
                sys.exit(-1)
            srv_list.append(
                {
                    "name": prj,
                    "ref": ref,
                }
            )

        return srv_list

    def freeze(self, qa_hash):
        body = {"operation": "freeze"}
        logger.debug(json.dumps(body))
        r = self._execute("PUT", f"/api/v1/qa/{qa_hash}", body=json.dumps(body))
        logger.info("QA freezing initiated")
        logger.debug(json.dumps(r.json(), indent=2))

    def unfreeze(self, qa_hash):
        body = {"operation": "unfreeze"}
        logger.debug(json.dumps(body))
        r = self._execute("PUT", f"/api/v1/qa/{qa_hash}", body=json.dumps(body))
        logger.info("QA unfreezing initiated")
        logger.debug(json.dumps(r.json(), indent=2))

    def maintenance(self):
        r = self._execute("POST", "/api/v1/maintenance")
        if r.json()["success"]:
            maintenance = r.json()["maintenance"]
            logger.info(
                f"Maintenance mode is now {'enabled' if maintenance else 'disabled'}"
            )

        logger.debug(json.dumps(r.json(), indent=2))

    def force_update(self, qa_hash):
        r = self._execute("POST", f"/api/v1/qa/shit-shoveler/force-update/{qa_hash}")
        if r.status_code == 400:
            logger.error("QA is not in a stale state")
            return
        if r.status_code == 500:
            logger.error("Something went wrong")
            return
        logger.info("QA has been forced to update")
        logger.debug(json.dumps(r.json(), indent=2))

    def _execute(self, request_method, api_endpoint, body=None):
        api_url = self.url + api_endpoint
        auth0_token = self._config.get_cache(f"{self.auth0_tenant}_auth0_token")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth0_token}",
        }
        logger.debug(request_method)
        logger.debug(api_url)
        logger.debug(headers)
        logger.debug(body)
        r = requests.request(request_method, api_url, headers=headers, data=body)

        if 200 <= r.status_code <= 299:
            logger.debug("Call to qainit-evo executed successfully")
        else:
            logger.error("Some issue during call to qainit-evo: ")
            logger.error(f"Status code: {r.status_code}, response: {r.text}")
            logger.error(api_endpoint)

        return r
