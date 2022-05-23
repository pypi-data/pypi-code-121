# -*- coding: utf-8 -*-

from suite_py.lib import logger
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler.drone_handler import DroneHandler
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler
from suite_py.lib.symbol import CHECKMARK, CROSSMARK


class Check:
    def __init__(self, config, tokens):
        self._checks = [
            ("Github", self._check_github),
            ("Drone", self._check_drone),
            ("Youtrack", self._check_youtrack),
            ("CaptainHook", self._check_captainhook),
            ("AWS", self._check_aws),
        ]
        self.config = config
        self._invalid_or_missing_tokens = []
        self._tokens = tokens
        self._youtrack = YoutrackHandler(config, tokens)
        self._github = GithubHandler(tokens)
        self._captainhook = CaptainHook(config)
        self._drone = DroneHandler(config, tokens)

    def run(self):
        # Services
        for service, check in self._checks:
            _forge_message(service, check())

        # Tokens
        if len(self._invalid_or_missing_tokens) > 0 and prompt_utils.ask_confirm(
            "Do you want to reinsert the missing tokens?", default=True
        ):
            self._refresh_tokens()

    def _check_github(self):
        if self._tokens.github:
            try:
                if self._github.get_organization():
                    return "ok"
                self._invalid_or_missing_tokens.append("github")
                return "invalid_token"
            except Exception:
                self._invalid_or_missing_tokens.append("github")
                return "invalid_token"
        else:
            self._invalid_or_missing_tokens.append("github")
            return "missing_token"

    def _check_drone(self):
        if self._tokens.drone:
            try:
                drone_user = self._drone.get_user()
                if "message" in drone_user and drone_user["message"] == "Unauthorized":
                    self._invalid_or_missing_tokens.append("drone")
                    return "invalid_token"
                return "ok"
            except Exception:
                self._invalid_or_missing_tokens.append("drone")
                return "invalid_token"
        else:
            self._invalid_or_missing_tokens.append("drone")
            return "missing_token"

    def _check_youtrack(self):
        if self._tokens.youtrack:
            try:
                self._youtrack.get_projects()
                return "ok"
            except Exception:
                self._invalid_or_missing_tokens.append("youtrack")
                return "invalid_token"
        else:
            self._invalid_or_missing_tokens.append("youtrack")
            return "missing_token"

    def _check_captainhook(self):
        try:
            if self._captainhook.check().status_code != 200:
                return "unreachable"
            return "ok"
        except Exception:
            return "unreachable"

    def _check_aws(self):
        try:
            if self.config.aws != "":
                return "ok"
            return "missing_token"
        except Exception:
            return "missing_token"

    def _refresh_tokens(self):
        for service in self._invalid_or_missing_tokens:
            new_token = prompt_utils.ask_questions_input(
                f"Enter new token for {service}: "
            )
            self._tokens.edit(service, new_token)

        logger.info("Saving the new tokens ...")
        self._tokens.save()
        logger.info(f"{CHECKMARK} Done!")


def _forge_message(service, result):
    cases = {
        "ok": f"{service:>12}:{CHECKMARK:>12} ok",
        "invalid_token": f"{service:>12}:{CROSSMARK:>12} token not valid",
        "missing_token": f"{service:>12}:{CROSSMARK:>12} missing token",
        "unreachable": f"{service:>12}:{CROSSMARK:>12} unreachable",
    }
    print(cases.get(result, f"{service}: unknown state"))
