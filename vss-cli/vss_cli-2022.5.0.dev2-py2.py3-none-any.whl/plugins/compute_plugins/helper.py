"""Helper module for the vss-cli compute plugins."""
from typing import Dict, Optional, Tuple, Union

import click


def process_retirement_new(
    retire_type: str,
    retire_value: Union[Tuple[int, int, int], str],
    retire_warning: Optional[int] = None,
) -> Dict:
    """Process retirement for new vm commands."""
    if not all([retire_type, retire_value]):
        raise click.BadParameter(
            'Retirement settings require at least: '
            '--retire-type and --retire-value'
        )
    if retire_type == 'timedelta':
        retire = {
            'value': {
                'type': retire_type,
                'hours': retire_value[0],
                'days': retire_value[1],
                'months': retire_value[2],
            }
        }
    else:
        retire = {'value': {'type': retire_type, 'datetime': retire_value}}
    if retire_warning:
        retire['warning'] = {'days': retire_warning}
    else:
        confirmation = click.confirm(
            'No warning will be sent for confirmation or cancellation. \n'
            'Retirement request will proceed when specified. \n'
            'Are you sure?'
        )
        if not confirmation:
            raise click.ClickException('Cancelled by user.')
    return retire
