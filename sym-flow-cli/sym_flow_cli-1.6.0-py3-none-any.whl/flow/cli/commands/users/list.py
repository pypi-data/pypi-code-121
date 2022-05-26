import click
from tabulate import tabulate

from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.helpers.users import UserUpdateSet


@click.command(
    name="list",
    short_help="List your Users",
)
@click.option(
    "-o",
    "--output-file",
    type=click.Path(exists=False),
    help="Save results to a CSV file",
)
@click.make_pass_decorator(GlobalOptions, ensure=True)
def users_list(options: GlobalOptions, output_file: str) -> None:
    """Prints a table view of Sym Users in your Organization and their corresponding identities to STDOUT.
    Use the --output-file option to save the results to a file in CSV format.

    To modify users, use `symflow users update`.
    """
    user_data = get_user_data(options.sym_api)
    if output_file:
        user_data.write_to_csv(output_file)
        click.echo(f"Saved {len(user_data.users)} users to {output_file}.")
    else:
        click.echo(tabulate_user_data(user_data))


def tabulate_user_data(user_data: UserUpdateSet) -> str:
    headers = user_data.headers
    headers.remove("User ID")
    return tabulate(user_data.tabulate(), headers=headers)


def get_user_data(api: SymAPI) -> UserUpdateSet:
    return UserUpdateSet(user_data=api.get_users(), service_data=api.get_services())
