"""Account Management plugin for VSS CLI (vss-cli)."""
import logging
from pathlib import Path
import sys
from typing import Tuple

import click

from vss_cli import autocompletion, const
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.utils.emoji import EMOJI_UNICODE
from vss_cli.validators import validate_phone_number

ej_tada = EMOJI_UNICODE.get(':party_popper:')
ej_mail = EMOJI_UNICODE.get(':closed_mailbox_with_raised_flag:')

_LOGGING = logging.getLogger(__name__)


def get_endpoint_and_creds(ctx: Configuration) -> Tuple[str, str, str]:
    """Get endpoint credentials."""
    endpoint = ctx.endpoint or click.prompt(
        'Endpoint',
        default=const.DEFAULT_ENDPOINT,
        type=click.STRING,
        show_default=True,
        err=True,
    )
    username = ctx.username or click.prompt(
        'Username',
        default=ctx.username,
        show_default=True,
        type=click.STRING,
        err=True,
    )
    password = ctx.password or click.prompt(
        'Password',
        default=ctx.password,
        show_default=False,
        hide_input=True,
        type=click.STRING,
        confirmation_prompt=True,
        err=True,
    )
    return endpoint, username, password


@click.group('account', short_help='Manage your VSS account')
@click.option(
    '--no-load', is_flag=True, default=False, help='do not load config'
)
@pass_context
def cli(ctx: Configuration, no_load: bool):
    """Manage your VSS account."""
    with ctx.spinner(disable=ctx.debug):
        if not no_load:
            ctx.load_config()


@cli.group('get', short_help='get account attribute')
@pass_context
def account_get(ctx: Configuration):
    """Obtain an account attribute."""
    pass


@account_get.group('digest')
@pass_context
def account_get_digest(ctx):
    """Get digest status."""
    pass


@account_get_digest.command('message')
@pass_context
def account_get_digest_message(ctx: Configuration):
    """Get message digest status."""
    with ctx.spinner(disable=ctx.debug):
        _obj = ctx.get_user_digest_settings()
    obj = {'message': _obj.get('message')}
    columns = ctx.columns or const.COLUMNS_MESSAGE_DIGEST
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@account_get.command('mfa')
@pass_context
def account_get_mfa(ctx: Configuration):
    """Get MFA account settings."""
    with ctx.spinner(disable=ctx.debug):
        _obj = ctx.get_user_totp()
    columns = ctx.columns or const.COLUMNS_USER_MFA
    ctx.echo(format_output(ctx, [_obj], columns=columns, single=True))


@account_get.command('groups')
@pass_context
def account_get_groups(ctx: Configuration):
    """User group membership."""
    with ctx.spinner(disable=ctx.debug):
        objs = ctx.get_user_groups(per_page=20)
    columns = ctx.columns or const.COLUMNS_GROUPS
    ctx.echo(format_output(ctx, objs, columns=columns))


@account_get.group('group', invoke_without_command=True)
@click.argument(
    'group_id_or_name',
    type=click.STRING,
    required=True,
    shell_complete=autocompletion.groups,
)
@pass_context
def account_get_group(ctx: Configuration, group_id_or_name):
    """Get given group info or members.

    User must be part of the group.
    """
    _group = ctx.get_vss_groups_by_name_desc_or_id(group_id_or_name)
    ctx.group = _group[0]['id']
    if click.get_current_context().invoked_subcommand is None:
        with ctx.spinner(disable=ctx.debug):
            obj = ctx.get_group(ctx.group)
        columns = ctx.columns or const.COLUMNS_GROUP
        ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@account_get_group.command('member')
@pass_context
def account_get_group_members(ctx: Configuration):
    """Get group members."""
    with ctx.spinner(disable=ctx.debug):
        objs = ctx.get_group_members(ctx.group)
    columns = ctx.columns or const.COLUMNS_GROUP_MEMBERS
    ctx.echo(format_output(ctx, objs, columns=columns))


@account_get.command('access-role')
@pass_context
def account_get_access_role(ctx: Configuration):
    """Access role and entitlements."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_roles()
    columns = ctx.columns or const.COLUMNS_ROLE
    ctx.echo(format_output(ctx, [obj['access']], columns=columns, single=True))


@account_get.command('request-role')
@pass_context
def account_get_request_role(ctx: Configuration):
    """Request role and entitlements."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_roles()
    columns = ctx.columns or const.COLUMNS_ROLE
    ctx.echo(
        format_output(ctx, [obj['request']], columns=columns, single=True)
    )


@account_get.command('personal')
@pass_context
def account_get_personal(ctx: Configuration):
    """Get user information."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_personal()
    obj.update(ctx.get_user_ldap())
    columns = ctx.columns or const.COLUMNS_USER_PERSONAL
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@account_get.command('status')
@pass_context
def account_get_pstatus(ctx: Configuration):
    """Get account status."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_status()
    columns = ctx.columns or const.COLUMNS_USER_STATUS
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@account_get.group('notification')
@pass_context
def account_get_notification(ctx: Configuration):
    """Get notification settings."""
    pass


@account_get_notification.command('request')
@pass_context
def account_get_notification_request(ctx: Configuration):
    """Get notification format."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_request_notification_settings()
    columns = ctx.columns or const.COLUMNS_NOT_REQUEST
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@account_get_notification.command('format')
@pass_context
def account_get_notification_format(ctx: Configuration):
    """Get notification format."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_notification_format()
    ctx.echo(format_output(ctx, [obj], columns=ctx.columns, single=True))


@account_get_notification.command('method')
@pass_context
def account_get_notification_method(ctx: Configuration):
    """Get notification format."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_notification_method()
    ctx.echo(format_output(ctx, [obj], columns=ctx.columns, single=True))


@cli.group('set', short_help='set account attribute')
@pass_context
def account_set(ctx: Configuration):
    """Set account attribute."""
    pass


@account_set.group(
    'digest', short_help='set account weekly digest configuration'
)
@pass_context
def account_set_digest(ctx: Configuration):
    """Update weekly digest configuration."""
    pass


@account_set_digest.command('message')
@click.argument('state', type=click.Choice(['in', 'out']), required=True)
@pass_context
def account_set_digest_message(ctx: Configuration, state):
    """Opt-in or opt-out of weekly message digest."""
    with ctx.spinner(disable=ctx.debug):
        if state == 'in':
            ctx.enable_user_message_digest()
        else:
            ctx.disable_user_message_digest()
    _obj = ctx.get_user_digest_settings()
    obj = {'message': _obj.get('message')}
    columns = ctx.columns or const.COLUMNS_MESSAGE_DIGEST
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@account_set.group(
    'notification', short_help='set account notification settings'
)
@pass_context
def account_notification_set(ctx: Configuration):
    """Set account notification settings."""
    pass


@account_notification_set.command('request')
@click.argument(
    'notification_type',
    type=click.Choice(['all', 'none', 'error', 'completion', 'submission']),
    nargs=-1,
    required=True,
)
@pass_context
def account_notification_set_request(ctx: Configuration, notification_type):
    """Customize request notification settings."""
    lookup = {
        'all': ctx.enable_user_request_all_notification,
        'none': ctx.disable_user_request_all_notification,
        'error': ctx.enable_user_request_error_notification,
        'submission': ctx.enable_user_request_submission_notification,
        'completion': ctx.enable_user_request_completion_notification,
    }
    for n_type in notification_type:
        try:
            f = lookup[n_type]
            f()
            if n_type in ['all', 'none']:
                status = 'enabled' if n_type == 'all' else 'disabled'
                ctx.secho(
                    f'Notifications triggered by requests '
                    f'have been {status}.',
                    fg='green',
                )
            elif n_type in ['error', 'submission', 'completion']:
                ctx.secho(
                    f'Notifications triggered by request {n_type} '
                    f'have been enabled.',
                    fg='green',
                )
        except KeyError:
            pass
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_request_notification_settings()
    columns = ctx.columns or const.COLUMNS_NOT_REQUEST
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@account_notification_set.command('format')
@click.argument('fmt', type=click.Choice(['html', 'text']), required=True)
@pass_context
def account_notification_set_format(ctx: Configuration, fmt):
    """Update notification format where FMT can be html or text."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.update_user_notification_format(fmt)
    ctx.echo(format_output(ctx, [obj], columns=ctx.columns, single=True))


@account_notification_set.command('method')
@click.argument(
    'method', type=click.Choice(['mail', 'message']), required=True
)
@pass_context
def account_notification_set_method(ctx: Configuration, method):
    """Update notification method where METHOD can be mail or message."""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.update_user_notification_method(method)
    ctx.echo(format_output(ctx, [obj], columns=ctx.columns, single=True))


@account_set.group('mfa', short_help='mfa account settings')
@pass_context
def mfa_set(ctx: Configuration):
    """Set account MFA settings."""
    pass


@mfa_set.command('rm')
@pass_context
def mfa_rm(ctx: Configuration):
    """Disable existing MFA setup."""
    endpoint, username, password = get_endpoint_and_creds(ctx)
    ctx.endpoint = endpoint
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.disable_totp(user=username, password=password)
    ctx.set_defaults()
    columns = ctx.columns or const.COLUMNS_MFA_MIN
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    rm_tk = click.prompt(
        'You should have received an email with a confirmation token. \n'
        'Please, paste the token to continue'
    )
    if rm_tk is not None:
        with ctx.spinner(disable=ctx.debug):
            obj = ctx.disable_totp_confirm(
                token=rm_tk, user=username, password=password
            )
        ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@mfa_set.command('get-token')
@pass_context
def mfa_request_token(ctx: Configuration):
    """Request TOTP token."""
    endpoint, username, password = get_endpoint_and_creds(ctx)
    try:
        ctx.endpoint = endpoint
        with ctx.spinner(disable=ctx.debug):
            _ = ctx.request_totp(user=username, password=password)
        ctx.secho(
            f'\nVerification code requested {ej_mail}.\n',
            file=sys.stderr,
            fg='green',
        )
    except Exception as ex:
        _LOGGING.error(f'Could not verify TOTP setup: {ex}')


@mfa_set.command('verify')
@click.argument('otp', type=click.STRING, required=False)
@pass_context
def mfa_verify(ctx: Configuration, otp):
    """Verify existing MFA setup."""
    endpoint, username, password = get_endpoint_and_creds(ctx)
    totp = otp or click.prompt(
        'TOTP Code', hide_input=False, type=click.STRING, err=True,
    )

    try:
        ctx.endpoint = endpoint
        with ctx.spinner(disable=ctx.debug):
            obj = ctx.verify_totp(user=username, password=password, otp=totp)
        ctx.secho(
            f'Verification complete: {obj.get("message")}'
            f'{EMOJI_UNICODE.get(":white_heavy_check_mark:")}\n',
            file=sys.stderr,
            fg='green',
        )
    except Exception as ex:
        _LOGGING.error(f'Could not verify TOTP setup: {ex}')


@mfa_set.command('mk')
@click.argument(
    'method',
    type=click.Choice(['EMAIL', 'AUTHENTICATOR', 'SMS']),
    required=True,
)
@click.option(
    '--phone',
    type=click.STRING,
    help='phone number to receive SMS',
    callback=validate_phone_number,
    required=False,
)
@pass_context
def mfa_mk(ctx: Configuration, method: str, phone: str):
    """Enable MFA with Time-based One-Time Password."""
    if method == 'SMS' and phone is None:
        raise click.BadParameter('--phone is required when using SMS')
    endpoint, username, password = get_endpoint_and_creds(ctx)
    ctx.endpoint = endpoint
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.enable_totp(
            user=username, password=password, method=method, phone=phone
        )
    recovery_codes = obj.get('recovery_codes')
    issuer = obj.get('issuer')
    if method == 'AUTHENTICATOR':
        uri = obj.get('uri')
        key = obj.get('key')
        _ = obj.get('image')
        import qrcode

        qr = qrcode.QRCode()
        qr.add_data(uri)
        qr.make(fit=True)
        if click.confirm(
            'Do you have a phone to scan a QR Code to generate TOTP codes?'
        ):
            qr.print_ascii(out=sys.stderr, invert=True)
        if click.confirm('Do you like to display the security key?'):
            ctx.secho(
                'Use the following key if you are unable '
                'to scan the QR Code:\n',
                file=sys.stderr,
                nl=True,
            )
            ctx.secho(
                f'{key}\n', file=sys.stderr, fg='blue', nl=True,
            )
    # print recovery codes.
    if recovery_codes is not None:
        ctx.secho(
            'Recovery codes are used to access your account in \n'
            'the event you cannot get two-factor authentication codes.\n',
            file=sys.stderr,
            nl=True,
        )
        rec_code_txt = '\n'.join(recovery_codes)
        ctx.secho(f'{rec_code_txt}\n', file=sys.stderr, nl=True, fg='blue')
        rec_code_obj = Path(f'{username}_{issuer}_recovery_codes.txt')
        if click.confirm('Would you like to save the codes into a text file?'):
            rec_code_obj.write_text(rec_code_txt)
            click.echo(f'Written {rec_code_obj} with recovery codes.')
    # verify
    if method in ['SMS', 'EMAIL']:
        _ = ctx.request_totp(user=username, password=password)
        ctx.secho(
            f'\nVerification code requested {ej_mail}.\n',
            file=sys.stderr,
            fg='green',
        )
    otp = click.prompt(
        '\nEnter the 6-digit Code to verify enrolment was successful',
        hide_input=False,
        type=click.STRING,
        err=True,
    )
    try:
        obj = ctx.verify_totp(user=username, password=password, otp=otp)
        ctx.secho(
            f'\nVerification complete: {obj.get("message")}'
            f'{EMOJI_UNICODE.get(":white_heavy_check_mark:")}\n',
            file=sys.stderr,
            fg='green',
        )
        success = True
    except Exception as ex:
        success = False
        _LOGGING.error(f'Could not verify TOTP setup: {ex}')
    if success:
        ctx.secho(
            f'You are ready to use the vss-cli '
            f'with MFA via {method} {ej_tada}',
            file=sys.stderr,
            fg='green',
        )
