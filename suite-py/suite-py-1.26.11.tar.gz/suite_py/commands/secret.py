# -*- coding: utf-8 -*-
import json
import os
import sys

import yaml

from suite_py.lib import logger
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.vault_handler import VaultHandler

profiles_mapping = {
    "common": {
        "stack_name_pattern": "{service}-platform-cluster-{env}-serviceaccount-iamrole",
        "logical_id": "ServiceAccountIamRole",
        "developer_role": "arn:aws:iam::595659439703:role/aws-reserved/sso.amazonaws.com/eu-west-1/AWSReservedSSO_ItalyDeveloperPlatform_cb5de4d001016cc4",
    },
    "it": {
        "stack_name_pattern": "ecs-roles-{service}-{env}",
        "logical_id": "ECSTaskRole",
        "developer_role": "arn:aws:iam::001575623345:role/AllowNonProductionBiscuitDecryption",
    },
    "uk": {
        "stack_name_pattern": "{service}-main-{env}-serviceaccount-iamrole",
        "logical_id": "ServiceAccountIamRole",
        "developer_role": "arn:aws:iam::815911007681:role/aws-reserved/sso.amazonaws.com/eu-west-1/AWSReservedSSO_UnitedKingdomDeveloper_f578b0b2b98ea593",
    },
    "es": {
        "stack_name_pattern": "{service}-main-{env}-serviceaccount-iamrole",
        "logical_id": "ServiceAccountIamRole",
        "developer_role": "arn:aws:iam::199959896441:role/aws-reserved/sso.amazonaws.com/eu-west-1/AWSReservedSSO_SpainDeveloper_acf53aa98cfc0ac4",
    },
}


class Secret:
    def __init__(self, project, config, action, base_profile):
        self._project = project
        self._config = config
        self._path = os.path.join(config.user["projects_home"], project)
        self._vault = VaultHandler(project, config)
        self._action = action
        self._base_profile = base_profile

    def run(self):
        if self._base_profile is not None:
            self._config.vault["base_secret_profile"] = self._base_profile

        if self._action == "create":
            self._create_new_secret()
            return

        if self._action == "grant":
            secrets = self._get_available_secrets()
            secret = prompt_utils.ask_choices("Select secret: ", secrets)
            self._set_grant_on_secret(secret)
            return

        logger.error(
            "You have to specify what to do! See available flags with suite-py secret --help"
        )

    def _create_new_secret(self):
        secret = prompt_utils.ask_questions_input("Enter secret name: ")
        value = prompt_utils.ask_questions_input("Enter secret value: ")
        e = self._vault.exec(
            self._config.vault["base_secret_profile"],
            f"biscuit put -f config/secrets.yml {secret} {value}",
        )
        if e.returncode != 0:
            logger.error("An error occurred.")
            sys.exit(1)

        if prompt_utils.ask_confirm(f"Do you want to grant permissions for {secret}?"):
            self._set_grant_on_secret(secret)
            return

    def _set_grant_on_secret(self, secret_name):
        environment = self._ask_environment()
        profiles = self._ask_profile()
        for profile in profiles:
            mapping = profiles_mapping[profile]
            stack_name = (
                mapping["stack_name_pattern"]
                .replace("{service}", self._project)
                .replace("{env}", environment)
            )
            # Get stack resource info
            logger.info(
                f"Obtaining ARN for {mapping['logical_id']} from stack {stack_name}..."
            )
            stack_resource = self._get_stack_resource(
                profile, stack_name, mapping["logical_id"]
            )
            if stack_resource is None:
                iam_role_arn = self._manual_iam_arn()
            else:
                iam_role_name = stack_resource["StackResourceDetail"][
                    "PhysicalResourceId"
                ]
                # Get IAM Role ARN
                iam_role = self._get_iam_role(profile, iam_role_name)
                iam_role_arn = iam_role["Role"]["Arn"]
                if iam_role_arn is None:
                    iam_role_arn = self._manual_iam_arn()
                logger.info(f"ARN found for profile {profile}: {iam_role_arn}")

            if iam_role_arn is None:
                continue

            logger.debug(
                f"---\nGranting permissions on {self._project}/{secret_name}\nEnvironment: {environment}\nUsing vault profile: {profile}\nIAM Role ARN: {iam_role_arn}\n---"
            )
            if not prompt_utils.ask_confirm("Do you want to continue?", default=True):
                continue

            # Grant decrypt permissions to task
            logger.info("Granting permissions to task...")
            e = self._vault.exec(
                self._config.vault["base_secret_profile"],
                f"biscuit kms grants create --grantee-principal {iam_role_arn} -f config/secrets.yml {secret_name}",
            )
            if e.returncode != 0:
                logger.error("An error occurred.")
                continue

            # Grant decrypt permissions to developers group
            if environment in ["staging", "qa"]:
                logger.info("Granting permissions to devs...")
                e = self._vault.exec(
                    self._config.vault["base_secret_profile"],
                    f"biscuit kms grants create --grantee-principal {mapping['developer_role']} -f config/secrets.yml {secret_name}",
                )
                if e.returncode != 0:
                    logger.error("An error occurred.")
                    continue

        logger.info("Ta-da! Permissions granted.")

    def _get_available_secrets(self):
        try:
            secrets = []
            with open(f"{self._path}/config/secrets.yml", encoding="utf-8") as s:
                yaml_secrets = yaml.load(s, Loader=yaml.FullLoader)
                secrets = [
                    key for key, values in yaml_secrets.items() if key != "_keys"
                ]

            return secrets
        except FileNotFoundError:
            logger.error("Can't load secrets from config/secrets.yml.")
            sys.exit(1)

    def _get_stack_resource(self, profile, stack_name, logical_id):
        e = self._vault.exec(
            profile,
            f"aws cloudformation describe-stack-resource --stack-name {stack_name} --logical-resource-id {logical_id}",
        )
        command_result = e.stdout.read()
        if e.returncode != 0:
            logger.warning("An error occurred trying to obtain stack. Skipping...")
            return None
        stack_info = command_result.decode("utf8").replace("'", '"')
        data = json.loads(stack_info)
        return data

    def _get_iam_role(self, profile, iam_role_name):
        e = self._vault.exec(
            profile,
            f"aws iam get-role --role-name {iam_role_name}",
            additional_args="--no-session",
        )
        command_result = e.stdout.read()
        if e.returncode != 0:
            logger.warning(
                "An error occurred trying to obtain IAM Role details. Skipping..."
            )
            return None
        stack_info = command_result.decode("utf8").replace("'", '"')
        data = json.loads(stack_info)
        return data

    def _manual_iam_arn(self):
        arn = prompt_utils.ask_questions_input(
            "No associated IAM Role ARN found. Insert it manually or leave blank to skip",
            default_text="",
        )
        if arn == "":
            return None
        return arn

    def _ask_environment(self):
        return prompt_utils.ask_choices(
            "Select an environment:", ["production", "staging", "qa"]
        )

    def _ask_profile(self):
        return prompt_utils.ask_multiple_choices(
            "Select vault profile(s):", self._config.vault["profiles"]
        )
