"""
Common commands
"""
import click

from montecarlodata.tools import convert_uuid_callback

RESOURCE_VERBIAGE = 'This can be helpful if the resource and collector are in different accounts'

DISAMBIGUATE_DC_OPTIONS = [
    click.option('--collector-id', 'dc_id', required=False, type=click.UUID, callback=convert_uuid_callback,
                 help='ID for the data collector. To disambiguate accounts with multiple collectors.'),
]

DC_RESOURCE_OPTIONS = [
    click.option('--resource-aws-region', required=False,
                 help='Override the AWS region where the resource is located. '
                      'Defaults to the region where the collector is hosted.'),
    click.option('--resource-aws-profile', required=False,
                 help=f'Override the AWS profile use by the CLI for the resource. {RESOURCE_VERBIAGE}.')
]