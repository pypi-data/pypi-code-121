import click

from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.models import ServiceType


@click.command(name="delete", short_help="Delete a Sym Bot User")
@click.make_pass_decorator(GlobalOptions, ensure=True)
@click.argument("username")
def bots_delete(options: GlobalOptions, username: str) -> None:
    """
    Deletes a Bot User with the given username and revokes all their tokens.
    """
    payload = {
        "users": [
            {
                "identity": {
                    "service_type": ServiceType.SYM.type_name,
                    "matcher": {"username": username},
                },
            }
        ]
    }

    options.sym_api.delete_user(payload)
    click.secho(f"Successfully deleted bot user {username}!", fg="green")
