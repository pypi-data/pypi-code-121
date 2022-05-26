from typing import List

from inquirer.questions import Checkbox

from sym.flow.cli.helpers.iam_policies import IAMPolicies
from sym.flow.cli.helpers.questions import ask


def format_actions(service: str, actions: List[str]) -> str:
    truncated = [action.split(":")[-1] for action in actions[:2]]
    return f"{service} ({', '.join(truncated)}, ...)"


def checkbox_for_access_levels(service: str) -> Checkbox:
    choices = [
        (format_actions(k, v), k)
        for k, v in IAMPolicies.actions_for_service(service).items()
        if v
    ]
    return Checkbox(
        name=service, message=f"Select {service} access levels", choices=choices
    )


def prompt_for_access_levels(service: str):
    return ask([checkbox_for_access_levels(service)])[service]
