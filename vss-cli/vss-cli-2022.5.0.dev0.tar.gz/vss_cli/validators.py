"""Validators module for the VSS-CLI."""
from datetime import datetime
import json
import logging
from pathlib import Path
import re
from uuid import UUID

import click

from vss_cli import const

_LOGGING = logging.getLogger(__name__)


def validate_phone_number(ctx, param, phone):
    """Validate phone number."""
    if phone:
        phone_regex = (
            r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|'
            r'\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d'
            r'{3}[-\.\s]??\d{4})+'
        )
        if not re.match(phone_regex, phone):
            raise click.BadParameter(
                'Value must be in the ' 'following format 416-166-6666'
            )
    return phone


def validate_email(ctx, param, email):
    """Validate email callback method."""
    email_regex = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+' r'\.[a-zA-Z0-9-.]+$)'
    if not re.match(email_regex, email):
        raise click.BadParameter(
            f'Value must be in the following format user@utoronto.ca: {email}'
        )
    return email


def flexible_email_args(ctx, param, value):
    """Validate multiple emails."""
    emails = []
    for val in value:
        if ',' in val:
            n_val = [i.strip() for i in val.split(',')]
            emails.extend(n_val)
        else:
            emails.append(val)
    for e in emails:
        validate_email(ctx, param, e)
    return emails


def validate_json_file_or_type(ctx, param, value):
    """Validate json file or type."""
    val = None
    try:
        if value is not None:
            val = json.loads(value)
    except ValueError as ex:
        _LOGGING.debug(f'Not string: {ex}')
        val = None
    try:
        if value is not None:
            p = Path(value)
            with p.open(encoding="UTF-8") as source:
                val = json.load(source)
    except FileNotFoundError as ex:
        _LOGGING.debug(f'Not file: {ex}')
        val = None

    if val is None:
        raise click.BadParameter(
            f'{param.name} should be a file or JSON parameter input.'
        )
    return val


def validate_json_type(ctx, param, value):
    """Validate json callback method."""
    try:
        if value is not None:
            return json.loads(value)
    except ValueError as ex:
        _LOGGING.error(f'{ex}')
        raise click.BadParameter(
            f'{param.name} should be a JSON parameter input.'
        )


def validate_admin(ctx, param, value):
    """Validate admin callback method."""
    if value:
        _value = value.split(':')
        if not value or len(_value) < 2:
            raise click.BadParameter(
                'Admin should be in the '
                'following format: '
                'FullName:Phone:email'
            )
        validate_email(ctx, param, _value[2])
        validate_phone_number(ctx, param, _value[1])
        return value


def validate_inform(ctx, param, value):
    """Validate inform callback method."""
    if value:
        _value = value.split(',')
        if not value:
            raise click.BadParameter(
                'Informational contacts format:'
                'email@utoronto.ca,email2@utoronto.ca'
            )
        for email in _value:
            validate_email(ctx, param, email)
        return value


def validate_uuid(ctx, param, value):
    """Validate uuid callback method."""
    if value:
        try:
            _ = UUID(value)
            return value
        except ValueError:
            return False


def validate_vm_moref(ctx, param, value):
    """Validate moref callback method."""
    if value:
        if re.match(r'vm-[0-9]+', value):
            return value
    return False


def retirement_value(ctx, param, value):
    """Process retirement value."""
    if value:
        tup = value.split(',')
        if len(tup) > 1:
            try:
                hours, days, months = value.split(',')
                hours = int(hours)
                days = int(days)
                months = int(months)
            except ValueError:
                raise click.BadParameter(
                    'Value format does not match: <hours>,<days>,<months>'
                )
            return hours, days, months
        else:
            try:
                _ = datetime.strptime(value, const.DEFAULT_DATETIME_FMT)
            except ValueError:
                raise click.BadParameter(
                    f"Value format does not match "
                    f"'{const.DEFAULT_DATETIME_FMT}'"
                )
            return value
    return value
