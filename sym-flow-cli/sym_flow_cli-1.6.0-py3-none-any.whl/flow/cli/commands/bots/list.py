from collections import Counter
from typing import List

import click
from tabulate import tabulate

from sym.flow.cli.helpers.api import SymAPI
from sym.flow.cli.helpers.global_options import GlobalOptions
from sym.flow.cli.helpers.utils import human_friendly, utc_to_local
from sym.flow.cli.models import BaseService, Service, ServiceType, User
from sym.flow.cli.models.user_type import UserType


@click.command(name="list", short_help="List all Sym Bot Users")
@click.make_pass_decorator(GlobalOptions, ensure=True)
def bots_list(options: GlobalOptions) -> None:
    """
    Lists all bot-users and their token counts in your organization.
    """
    table_data = get_bot_users_data(options.sym_api)
    click.echo(tabulate(table_data, headers="firstrow"))


def get_bot_users_data(api: SymAPI) -> List[List[str]]:
    bot_users = api.get_users({"type": UserType.BOT})
    services = _extract_services_from_user_data(bot_users)

    token_counts = Counter([str(t.user.id) for t in api.get_tokens()])
    headers = ["Username", "Token Count", "Created At"] + [
        service.service_key for service in services
    ]
    table_data = [headers]
    for u in bot_users:
        user_info = [
            u.sym_identifier,
            token_counts.get(u.id, 0),
            human_friendly(utc_to_local(u.created_at)),
        ]
        for service in services:
            user_info.append(u.identity_repr_for_service(service))
        table_data.append(user_info)

    return table_data


def _extract_services_from_user_data(user_data: List[User]) -> List[BaseService]:
    services = []
    for user in user_data:
        for identity in user.identities:
            if identity.service.service_type != ServiceType.SYM.type_name:
                services.append(identity.service)

    return services
