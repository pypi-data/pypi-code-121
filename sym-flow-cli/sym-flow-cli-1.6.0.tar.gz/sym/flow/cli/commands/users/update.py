import csv
import tempfile
from typing import Dict

import click

from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.api_operations import OperationHelper
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.helpers.users import UserUpdateSet
from sym.flow.cli.models.user import User


@click.command(name="update", short_help="Edit Users' Identities")
@click.option(
    "-i",
    "--input-file",
    type=click.Path(file_okay=True, dir_okay=False, exists=True),
    help="File to use as input data",
)
@click.make_pass_decorator(GlobalOptions, ensure=True)
def users_update(options: GlobalOptions, input_file: str) -> None:
    """Create, delete or modify Sym Users and their identities such as AWS SSO IDs.
    If no input file is provided, this will trigger an interactive prompt to edit data in CSV format.

    \b
    Example:
        `symflow users update --input-file my-users.csv`
    """

    api = options.sym_api

    users = api.get_users()
    services = api.get_services()
    initial_data = UserUpdateSet(user_data=users, service_data=services)

    if input_file:
        filename = input_file
    else:
        click.confirm(
            "WARNING: This will open an editor in which you can modify ALL of your existing Users and Identities as raw CSV data!\nAre you sure you want to continue?",
            abort=True,
            default=False,
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as csv_file:
            writer = csv.DictWriter(
                csv_file, fieldnames=initial_data.headers, quotechar="`"
            )
            writer.writeheader()
            for user in initial_data.users:
                writer.writerow(prepare_user_row(initial_data=initial_data, user=user))

        click.edit(filename=csv_file.name, require_save=True)
        filename = csv_file.name

    edited_data = UserUpdateSet(service_data=services)
    with open(filename) as csv_update_file:
        reader = csv.DictReader(csv_update_file, quotechar="`")
        row_count = 2  # Start at 1 and skip header row
        try:
            for row in reader:
                if extra_services := (
                    {s for s in row.keys() if s} - set(initial_data.headers)
                ):
                    click.secho(
                        f"The following Services were provided but do not exist: {', '.join(extra_services)}",
                        fg="red",
                    )
                    return

                if (
                    None in row.keys()
                ):  # DictReader puts values without headers into a list under None
                    click.secho(
                        f"Warning: row {row_count} had unexpected formatting. Please verify your data to ensure it is correct.",
                        fg="yellow",
                    )

                edited_data.add_csv_row(row)
                row_count += 1

        except StopIteration:
            click.echo("No CSV data was provided. Exiting!")
            return

    operations = UserUpdateSet.compare_user_sets(initial_data, edited_data)
    operation_helper = OperationHelper(options, operations=operations)
    operation_helper.apply_changes()


def prepare_user_row(initial_data: UserUpdateSet, user: User) -> Dict[str, str]:
    row = {}
    for service in initial_data.services:
        if service.service_type in initial_data.uneditable_service_types:
            continue
        repr_identity = user.identity_repr_for_service(service)
        row[service.service_key] = repr_identity
    row["User ID"] = user.id
    return row
