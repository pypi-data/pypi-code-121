from typing import Optional

import click
import inquirer
from inquirer.shortcuts import confirm, list_input
from policy_sentry.querying.all import get_all_service_prefixes
from policy_sentry.querying.arns import get_arn_type_details, get_arn_types_for_service
from policy_sentry.shared.iam_data import get_service_prefix_data
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.shortcuts import prompt

from sym.flow.cli.helpers.arn import RawARN
from sym.flow.cli.helpers.iam_policies import IAMPolicies
from sym.flow.cli.helpers.questions import ask

from .helpers import prompt_for_access_levels


def prompt_for_resource(policies: IAMPolicies, service):
    choices = get_arn_types_for_service(service).keys()
    resource = list_input(message="Select a resource to add", choices=choices)

    raw_arn = get_arn_type_details(service, resource)["raw_arn"]
    arn = RawARN(raw_arn)

    answers = ask(
        [
            inquirer.Text(name=field, message=f"Enter the {field}", default=default)
            for field, default in arn.values().items()
        ]
    )
    arn.update(answers)

    click.secho(f"Added {arn}\n", fg="green")
    policies.add_arn(str(arn))


@click.command(
    name="wizard",
    short_help="Interactively create an AWS IAM Policy",
)
@click.option("--service", help="The AWS Service to generate a policy for")
def policies_wizard(service: Optional[str]):
    services = get_all_service_prefixes()
    service_meta = {s: get_service_prefix_data(s)["service_name"] for s in services}
    completer = FuzzyWordCompleter(words=services, meta_dict=service_meta)
    service = prompt(
        "Enter an AWS Service: ",
        completer=completer,
        complete_while_typing=True,
        default=service or "",
    )

    levels = prompt_for_access_levels(service)

    policies = IAMPolicies()

    prompt_for_resource(policies, service)
    while confirm("Would you like to add another resource to the policy?"):
        prompt_for_resource(policies, service)

    policy = policies.policy_for(*levels)
    click.echo_via_pager(policy)
