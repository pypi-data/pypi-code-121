import json
from collections import defaultdict
from typing import Dict, List, Literal, Sequence

import inflection
from policy_sentry.querying.actions import get_actions_with_access_level
from policy_sentry.util.arns import get_service_from_arn
from policy_sentry.writing.sid_group import SidGroup
from sym.shared.cli.errors import CliError

from sym.flow.cli.helpers.arn import RawARN

# This class is used to support the `sym_resources` TF resource.
# Users can specify AWS resource ARNs to wrap a Sym workflow around,
# and this class can generate the appropriate read/write/admin policies
# for those resources, automatically.

ACTION_LEVELS = ["Read", "Write", "List", "Tagging", "Permissions management"]

PolicyAction = Literal["read", "write", "list", "tagging", "permissions-management"]
PolicySizeLimit = 2048


class IAMPolicies:
    @classmethod
    def actions_for_service(cls, service) -> Dict[str, List[str]]:
        return {al: get_actions_with_access_level(service, al) for al in ACTION_LEVELS}

    @classmethod
    def normalize_action(cls, action: str) -> PolicyAction:
        return inflection.parameterize(action)

    def __init__(self, name: str = ""):
        self.name = name
        self._arns: Dict[PolicyAction, List[str]] = defaultdict(list)
        self.sid_group = SidGroup()

    @property
    def arns(self) -> List[str]:
        return [arn for arns in self._arns.values() for arn in arns]

    def services(self) -> Dict[str, List[str]]:
        services = defaultdict(list)
        for arn in self.arns:
            services[get_service_from_arn(arn)].append(arn)
        return services

    def add_arn(self, arn: str, levels: List[str] = ACTION_LEVELS):
        if not arn.startswith("arn:"):
            arn = f"arn:{arn}"
        if not RawARN.validate(arn):
            raise CliError(f"Invalid ARN: {arn}")

        for action in levels:
            self._arns[self.normalize_action(action)].append(arn)

    def template(self, *actions: Sequence[PolicyAction], name: str) -> Dict[str, str]:
        template = {"mode": "crud", "name": f"{self.name}{name}"}
        for action in actions:
            normalized = self.normalize_action(action)
            template[normalized] = self._arns[normalized].copy()
        return template

    def policy_dict(self, template: dict):
        policy = self.sid_group.process_template(template)
        if len(json.dumps(policy).replace(" ", "")) > PolicySizeLimit:
            policy = self.sid_group.process_template(template, minimize=True)
        return policy

    def policy_for(self, *actions: Sequence[PolicyAction], name: str = ""):
        template = self.template(*actions, name=name)
        policy = self.policy_dict(template)
        return json.dumps(policy, indent=4)

    def read_policy(self):
        return self.policy_for("read", "list", name="ReadOnly")

    def write_policy(self):
        return self.policy_for("read", "list", "write", name="ReadWrite")

    def admin_policy(self):
        return self.policy_for(
            "read", "list", "write", "tagging", "permissions-management", name="Admin"
        )
