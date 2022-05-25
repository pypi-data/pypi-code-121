import os

import click
import inquirer
from sshpubkeys import InvalidKeyError, SSHKey

from vessl.cli._base import VesslGroup, vessl_option
from vessl.cli._util import print_table, prompt_choices, truncate_datetime
from vessl.ssh_key import create_ssh_key, delete_ssh_key, list_ssh_keys
from vessl.util.common import parse_time_to_ago
from vessl.util.constant import SSH_PUBLIC_KEY_PATH


def ssh_key_id_callback(ctx: click.Context, param: click.Parameter, value: id) -> id:
    ssh_keys = list_ssh_keys()
    return prompt_choices(
        "SSH key",
        [
            (
                f"{x.name} / {x.fingerprint} (created {parse_time_to_ago(x.created_dt)})",
                x.id,
            )
            for x in ssh_keys
        ],
    )


def ssh_public_key_value_callback(
    ctx: click.Context, param: click.Option, key_path: str
) -> str:
    if not key_path:
        key_path = inquirer.prompt(
            [
                inquirer.Text(
                    "question",
                    message="SSH public key path",
                    default=SSH_PUBLIC_KEY_PATH,
                )
            ],
            raise_keyboard_interrupt=True,
        ).get("question")

    try:
        with open(key_path, "r") as f:
            ssh_public_key_value = f.read()
    except FileNotFoundError:
        raise click.BadParameter("Key file not found")

    ssh = SSHKey(ssh_public_key_value, strict=True)
    try:
        ssh.parse()
    except InvalidKeyError as e:
        raise click.BadParameter(f"Invalid key: {e}")
    except NotImplementedError as e:
        raise click.BadParameter(f"Invalid key type: {e}")

    ctx.obj["ssh_key_name"] = ssh.comment
    ctx.obj["ssh_key_filename"] = os.path.basename(key_path)
    return ssh_public_key_value


def ssh_key_name_callback(ctx: click.Context, param: click.Option, name: str) -> str:
    if name:
        return name

    return inquirer.prompt(
        [
            inquirer.Text(
                "question",
                message="SSH public key name",
                default=ctx.obj.get("ssh_key_name"),
            )
        ],
        raise_keyboard_interrupt=True,
    ).get("question")


@click.command(name="ssh-key", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
def list():
    ssh_keys = list_ssh_keys()
    print_table(
        ssh_keys,
        ["Name", "Fingerprint", "Created"],
        lambda x: [x.name, x.fingerprint, truncate_datetime(x.created_dt)],
    )


@cli.vessl_command()
@vessl_option(
    "-p",
    "--path",
    "ssh_public_key_value",
    type=click.Path(exists=True),
    help="Path to SSH public key.",
    callback=ssh_public_key_value_callback,
)
@vessl_option(
    "--name",
    type=click.STRING,
    callback=ssh_key_name_callback,
)
@click.pass_context
def add(ctx: click.Context, name: str, ssh_public_key_value: str):
    ssh_key = create_ssh_key(
        key_name=name,
        key_path=ctx.obj["ssh_key_filename"],
        ssh_public_key_value=ssh_public_key_value,
    )
    print(f"SSH Key '{ssh_key.name}' created.")


@cli.vessl_command()
@vessl_option(
    "--id",
    type=click.INT,
    hidden=True,
    callback=ssh_key_id_callback,
)
def delete(id: int):
    delete_ssh_key(key_id=id)
    print("Successfully deleted.")
