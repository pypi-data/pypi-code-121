import click

from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.models.service import BaseService
from sym.flow.cli.models.user import CSVMatcher


@click.command(
    name="delete",
    short_help="Delete a User",
)
@click.argument("service", required=True, type=str)
@click.option("--user-id", required=True, type=str)
@click.make_pass_decorator(GlobalOptions, ensure=True)
def users_delete(options: GlobalOptions, service: str, user_id: str) -> None:
    # External ID is not used, using service as a placeholder
    service_obj = BaseService(slug=service, external_id=service)
    matcher = CSVMatcher(service=service_obj, value=user_id)

    payload = {
        "users": [
            {
                "identity": {
                    "service_type": service,
                    "matcher": matcher.to_dict(),
                },
            }
        ]
    }

    options.sym_api.delete_user(payload)
    click.secho(f"Successfully deleted user {user_id}!")
