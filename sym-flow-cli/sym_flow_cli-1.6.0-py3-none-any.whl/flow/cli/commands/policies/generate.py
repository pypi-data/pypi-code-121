import click
from inquirer.shortcuts import confirm, text
from policy_sentry.querying.arns import (
    get_matching_raw_arns,
    get_resource_type_name_with_raw_arn,
)
from policy_sentry.util.arns import get_service_from_arn

from sym.flow.cli.commands.policies.helpers import prompt_for_access_levels
from sym.flow.cli.helpers.arn import RawARN
from sym.flow.cli.helpers.iam_policies import IAMPolicies


def prompt_for_arn(policies: IAMPolicies):
    arn = text(message="Enter an ARN", validate=lambda _, x: RawARN.validate(x))
    service = get_service_from_arn(arn)
    resource = get_resource_type_name_with_raw_arn(get_matching_raw_arns(arn)[0])
    click.secho(f"\nFound a {service} {resource}!\n", fg="green")

    levels = prompt_for_access_levels(service)
    policies.add_arn(arn, levels)


@click.command(
    name="generate",
    short_help="Create an AWS IAM Policy from ARNs",
)
def policies_generate():
    policies = IAMPolicies()

    prompt_for_arn(policies)
    while confirm("Would you like to add another ARN?"):
        prompt_for_arn(policies)

    policy = policies.admin_policy()
    click.echo_via_pager(policy)
