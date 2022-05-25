#  Copyright 2022 Data Spree GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import csv
import logging
from typing import List, Dict

import click
import requests as rq

import dataspree.platform_sdk as sdk

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command('export')
@click.option('-o', '--output_dir', 'output_dir', required=True, help='Output directory.',
              type=click.Path(exists=False, file_okay=False))
@click.option('-i', '--id', 'dataset_id', required=False, default=-1, help='ID of the dataset to download.', type=int,
              prompt='Please enter the ID of the dataset to download')
@click.option('-n', '--n_items', required=False, default=-1,
              help='Number of items to download. Download all items: \'-1\'', show_default=True, type=int)
@click.option('--status', 'accepted_status', required=False, multiple=True,
              type=click.Choice(['', 'uploaded', 'annotated', 'reviewed', 'ignored']),
              help='Download only those dataset items with the given status.')
@click.option('--http_retries', required=False, default=10, help='Number of HTTP retries.', show_default=True, type=int)
@click.option('--parallel_requests', required=False, default=16, help='Number of parallel requests.', show_default=True,
              type=int)
@click.option('--username', prompt='Username', help='Username for data spree vision platform.', envvar='DS_USERNAME')
@click.option('--password', prompt='Password', hide_input=True, help='Password for data spree vision platform.',
              envvar='DS_PASSWORD')
@click.option('--url', 'server_url', default='https://api.vision.data-spree.com/api',
              help='URL to the API of the platform.', envvar='DS_SERVER_URL')
def export_command(output_dir, dataset_id, n_items, accepted_status, username, password, http_retries,
                   parallel_requests, server_url):
    client = sdk.Client(username, password, None, http_retries, parallel_requests, server_url)

    if len(accepted_status) == 0:
        accepted_status = None
    return client.download_dataset(output_dir, dataset_id, n_items, accepted_status)


@cli.command('export_dataset_items')
@click.option('-o', '--output_file', 'output_file', required=True, help='Output csv file.',
              type=click.Path(exists=False, dir_okay=False))
@click.option('-f', '--fields', 'fields', required=False, multiple=True)
@click.option('--http_retries', required=False, default=10, help='Number of HTTP retries.', show_default=True, type=int)
@click.option('--parallel_requests', required=False, default=16, help='Number of parallel requests.', show_default=True,
              type=int)
@click.option('--username', prompt='Username', help='Username for data spree vision platform.', envvar='DS_USERNAME')
@click.option('--password', prompt='Password', hide_input=True, help='Password for data spree vision platform.',
              envvar='DS_PASSWORD')
@click.option('--url', 'server_url', default='https://api.vision.data-spree.com/api',
              help='URL to the API of the platform.', envvar='DS_SERVER_URL')
@click.option('-i', '--id', 'dataset_id', required=False, default=-1, help='ID of the dataset to download.', type=int,
              prompt='Please enter the ID of the dataset to download')
@click.option('-s', '--status', 'status', required=False, multiple=True)
def export_dataset_items(output_file, fields, dataset_id, status, username, password, http_retries,
                         parallel_requests, server_url):
    client = sdk.Client(username, password, None, http_retries, parallel_requests, server_url)
    items: List[Dict] = client.get_dataset_items(dataset_id=dataset_id, status=list(status))
    # id, created_date, uploaded_date, name

    with open(output_file, 'w') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(map(str, fields))
        for item in items:
            writer.writerow(map(str, map(item.get, fields)))


@cli.command(name='import')
@click.option('--format', 'dataset_format', type=click.Choice(['dataspree', 'kitti', 'coco', 'class_subdirs']),
              default='dataspree',
              help='Dataset format to import')
@click.option('--dataset_name', help='Name of the newly created dataset.')
@click.option('--dataset_id', type=int, default=-1,
              help='ID of the dataset to which new items should be imported. If set to \'-1\', a new dataset will be created')
@click.option('--images', 'images', required=False, type=click.Path(exists=True),
              help='Directory containing the images to import.')
@click.option('--annotations', 'annotations', required=False, type=click.Path(exists=True),
              help='Directory or file containing the annotations to import.')
@click.option('--directory', 'directory', required=False, type=click.Path(exists=True),
              help='Directory or file containing data to import (only used for importing classification data from subdirectories).')
@click.option('--http_retries', required=False, default=10, help='Number of HTTP retries.', show_default=True, type=int)
@click.option('--parallel_requests', required=False, default=16, help='Number of parallel requests.', show_default=True,
              type=int)
@click.option('--username', prompt='Username', help='Username for data spree vision platform.', envvar='DS_USERNAME')
@click.option('--password', prompt='Password', hide_input=True, help='Password for data spree vision platform.',
              envvar='DS_PASSWORD')
@click.option('--url', 'server_url', default='https://api.vision.data-spree.com/api',
              help='URL to the API of the platform.', envvar='DS_SERVER_URL')
def import_command(dataset_format, dataset_id, dataset_name, images, annotations, directory, http_retries,
                   parallel_requests, username, password,
                   server_url):
    client = sdk.Client(username, password, None, http_retries, parallel_requests, server_url)
    if dataset_format == 'dataspree':
        return client.import_dataspree(dataset_name, dataset_id, images, annotations)
    elif dataset_format == 'kitti':
        return client.import_kitti(dataset_name, dataset_id, images, annotations)
    elif dataset_format == 'coco':
        return client.import_coco(dataset_name, dataset_id, images, annotations)
    elif dataset_format == 'class_subdirs':
        return client.import_classification_directories(dataset_name, dataset_id, directory)


@cli.group()
@click.option('--url', default='http://localhost:6714', help='Base URL to reach the worker.', envvar='DS_WORKER_URL')
@click.option('--timeout', default=5, help='Timeout for requests to the worker.')
@click.pass_context
def worker(ctx, url, timeout):
    ctx.ensure_object(dict)
    ctx.obj['url'] = url
    ctx.obj['timeout'] = timeout


@worker.command()
@click.pass_context
def pause(ctx):
    try:
        base_url = ctx.obj['url']
        timeout = ctx.obj['timeout']
        response = rq.get(f'{base_url}/pause', timeout=timeout)
        response.raise_for_status()
        click.echo('Pausing the worker has been initiated. It can take up to one minute until a training checkpoint is '
                   'created and the training stopped.')
    except rq.exceptions.HTTPError as e:
        click.echo(f'HTTP error: {e}')
    except rq.exceptions.RequestException as e:
        click.echo(f'Worker is offline. Make sure that the worker is running.')


@worker.command()
@click.pass_context
def resume(ctx):
    try:
        base_url = ctx.obj['url']
        timeout = ctx.obj['timeout']
        response = rq.get(f'{base_url}/resume', timeout=timeout)
        response.raise_for_status()
        click.echo('Worker has been resumed.')
    except rq.exceptions.HTTPError as e:
        click.echo(f'HTTP error: {e}')
    except rq.exceptions.RequestException as e:
        click.echo(f'Worker is offline. Make sure that the worker is running.')


@worker.command()
@click.pass_context
def status(ctx):
    try:
        base_url = ctx.obj['url']
        timeout = ctx.obj['timeout']
        response = rq.get(f'{base_url}/status', timeout=timeout)
        response.raise_for_status()
        worker_status = response.json()
        iteration = worker_status["iteration"]
        if iteration is None:
            iteration = '-'
        job = worker_status["job"]
        if job is None:
            job = '-'
        click.echo(f'status:\t{worker_status["status"]}\niteration:\t{iteration}\njob:\t{job}')
    except rq.exceptions.HTTPError as e:
        click.echo(f'HTTP error: {e}')
    except rq.exceptions.RequestException as e:
        click.echo(f'status:\toffline\niteration:\t-\njob:\t-')


def do_setup(base_url, timeout):
    try:
        # check server status
        response = rq.get(f'{base_url}/status', timeout=timeout)
        response.raise_for_status()

        worker_status = response.json()
        if worker_status['status'] != 'uninitialized':
            if not click.confirm(
                    'The worker is already initialized. Do you want to setup the worker anew? A new worker '
                    'instance will be created in the AI platform and running jobs will be stopped. This can '
                    'take a minute.'):
                return
        auth_method = click.prompt('Which authentication method should be used by the worker?',
                                   default='username/password',
                                   type=click.Choice(['username/password', 'token']))
        setup_data = {}
        if auth_method == 'username/password':
            setup_data['username'] = click.prompt('Username', type=str)
            setup_data['password'] = click.prompt('Password', type=str, hide_input=True)
        elif auth_method == 'token':
            setup_data['auth_token'] = click.prompt('Token', type=str)

        setup_data['platform_host'] = click.prompt('AI Platform Host', default='api.vision.data-spree.com', type=str)
        setup_data['dataset_dir'] = click.prompt('Dataset directory', default='', type=str)
        click.echo('Setting up...')
        response = rq.post(f'{base_url}/setup', json=setup_data, timeout=timeout)
        if response.status_code == 200:
            click.echo('Setup successful')
        else:
            click.echo(f'Setup failed: {response.text}')

    except rq.exceptions.HTTPError as e:
        click.echo(f'HTTP error: {e}')
    except rq.exceptions.RequestException as e:
        click.echo(f'Worker is offline. Make sure that the worker is running.')


@worker.command()
@click.pass_context
def setup(ctx):
    base_url = ctx.obj['url']
    timeout = ctx.obj['timeout']
    do_setup(base_url, timeout)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)-6s %(message)s')
    cli()
