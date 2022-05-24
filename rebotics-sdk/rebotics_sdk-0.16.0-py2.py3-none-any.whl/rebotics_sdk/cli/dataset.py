import json
import os
import pathlib
import shutil
from functools import partial
from multiprocessing.pool import Pool

import click
import requests
from tqdm import tqdm

from rebotics_sdk.cli.common import shell, configure, roles, set_token
from .utils import ReboticsCLIContext, pass_rebotics_context, app_dir, read_saved_role, process_role
from ..advanced import remote_loaders
from ..constants import DownloadImagesFormat
from ..providers import DatasetProvider, ProviderHTTPClientException
from ..providers.utils import get_id_list_from_ranges
from ..utils import download_file, mkdir_p, get_filename_from_url


@click.group()
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']))
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='dataset.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('dataset'), help="Key to specify what dataset to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role):
    """
    Dataset CLI tool to communicate with dataset API
    """
    process_role(ctx, role, 'dataset')
    ctx.obj = ReboticsCLIContext(
        role,
        format,
        verbose,
        os.path.join(app_dir, config),
        provider_class=DatasetProvider
    )


def save_image_task(d):
    download_file(d['url'], d['filepath'])
    click.echo('Downloaded jpeg image to {}'.format(d['filepath']))


@api.command()
@click.argument('meta_data_url', )
@click.option('-t', '--target', type=click.Path(), default='.')
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def setup_training_dir(ctx, meta_data_url, target, concurrency):
    """Set up training directory"""
    click.echo("Downloading meta data from {}".format(meta_data_url), err=True)
    response = requests.get(meta_data_url, timeout=remote_loaders.HTTP_TIMEOUTS)
    response.raise_for_status()

    meta_data = response.json()
    click.echo("Downloaded meta data from {}".format(meta_data_url), err=True)

    mkdir_p(target)
    annotations_path = os.path.join(target, 'Annotations')
    mkdir_p(annotations_path)
    images_path = os.path.join(target, 'JPEGImages')
    mkdir_p(images_path)
    image_sets_path = os.path.join(target, 'ImageSets')
    mkdir_p(image_sets_path)
    main_path = os.path.join(image_sets_path, 'Main')
    mkdir_p(main_path)

    for file_in_main in meta_data['main']:
        with open(os.path.join(main_path, file_in_main['filename']), 'w') as fout:
            fout.write(file_in_main['value'])

    for annotation_file in meta_data['annotations']:
        with open(os.path.join(annotations_path, annotation_file['filename']), 'w') as fout:
            fout.write(annotation_file['value'])

    click.echo("Saved annotation files. Fetching images...", err=True)

    p = Pool(concurrency)
    jpeg_images = [
        {
            'url': i['url'],
            'filepath': os.path.join(images_path, i['image_name'])
        } for i in meta_data['jpeg_images']
    ]
    p.map(save_image_task, jpeg_images)


def task_upload_feature_vector_batch(d):
    ctx, data, batch_index = d
    try:
        return ctx.provider.save_feature_vector_batch(data)
    except ProviderHTTPClientException as exc:
        return exc


@api.command()
@click.argument('ref_upc', type=click.File())
@click.argument('ref_features', type=click.File())
@click.argument('ref_threshold', type=click.File())
@click.option('-r', '--retailer', prompt=True, )
@click.option('-f', '--facenet', prompt=True, )
@click.option('-s', '--batch-size', default=100)
@click.option('-c', '--concurrency', type=int, default=4)
@pass_rebotics_context
def upload_ref(ctx, ref_upc, ref_features, ref_threshold, retailer, facenet, batch_size, concurrency):
    """Uploads reference UPC and reference features for retailer and facenet to dataset"""
    click.echo('Starting uploading to {provider.host} for {retailer} and {facenet}...'.format(
        provider=ctx.provider, retailer=retailer, facenet=facenet
    ), err=True)

    if ctx.verbose:
        click.echo('Generating batches')

    data_to_post = [
        ctx.provider.construct_reference_entry(
            upc=upc_code, feature=feature_vector, threshold=threshold,
            retailer=retailer, facenet=facenet,
        )
        for upc_code, feature_vector, threshold in zip(ref_upc, ref_features, ref_threshold)
    ]

    batches = []

    for batch_index in range(0, len(data_to_post), batch_size):
        batches.append(data_to_post[batch_index:batch_index + batch_size])

    if ctx.verbose:
        click.echo('Created {} batches'.format(len(batches)))

    pool = Pool(concurrency)

    result = []
    for res in tqdm(
        pool.imap_unordered(task_upload_feature_vector_batch, [(ctx, d, i) for i, d in enumerate(batches)]),
        total=len(batches)
    ):
        result.append(res)

    if ctx.verbose:
        click.echo(result)

    click.echo('Done uploading to {provider.host} for {retailer} and {facenet}!'.format(
        provider=ctx.provider, retailer=retailer, facenet=facenet
    ))


@api.command()
@click.option('-r', '--retailer', prompt=True, )
@click.option('-f', '--facenet', prompt=True, )
@click.argument('output', type=click.Path(), default='.')
@pass_rebotics_context
def download_ref_backup(ctx, retailer, facenet, output):
    """Downloads reference backup for retailer and facenet"""
    filename, raw = ctx.provider.download_reference_database(retailer, facenet)

    if os.path.isdir(output):
        mkdir_p(output)
        output = os.path.join(output, filename)
    elif os.path.isfile(output):
        mkdir_p(os.path.dirname(output))
    else:
        raise OSError('Could not write to path that does not')

    if ctx.verbose:
        click.echo(output)

    with open(output, 'wb') as out_file:
        shutil.copyfileobj(raw, out_file)


def task_download_and_set_training_data(item_id, target, format, ctx):
    try:
        response = ctx.provider.get_detection_image_by_id(item_id)
    except Exception:
        click.echo("Failed to find image with id={}".format(item_id))
        return
    # download images and download this json
    if format in (DownloadImagesFormat.FULL, DownloadImagesFormat.IMAGES):
        image_url = response['image']
        image_file = target / "{}.{ext}".format(
            item_id,
            ext=get_filename_from_url(image_url).split(".")[-1]
        )
        try:
            remote_loaders.download(image_url, str(image_file))
        except Exception:
            click.echo("{} failed to download image from {}".format(item_id, image_url))
    if format in (DownloadImagesFormat.FULL, DownloadImagesFormat.ANNOTATIONS):
        json_file = target / "{}.json".format(item_id)
        with open(str(json_file), 'w') as fio:
            json.dump(response, fio, indent=4)


@api.command()
@click.argument("image_ids", type=click.STRING)
@click.option('-t', '--target', type=click.Path(), default='.')
@click.option('-c', '--concurrency', type=int, default=4)
@click.option('-f', '--format',
              type=click.Choice(DownloadImagesFormat.OPTIONS, case_sensitive=False),
              default=DownloadImagesFormat.FULL, )
@pass_rebotics_context
def download_images(ctx, image_ids, target, concurrency, format):
    """Download images and/or annotations json."""
    # parse image_ids as range or as a ids
    id_list = get_id_list_from_ranges(image_ids)
    if ctx.verbose:
        click.echo(id_list)

    if not id_list:
        click.echo("Invalid ID list is supplied, failed to extract ids")

    mkdir_p(str(target))

    with Pool(min(len(id_list), concurrency)) as pool:
        pool.map(
            partial(task_download_and_set_training_data,
                    target=pathlib.Path(target),
                    format=format,
                    ctx=ctx, ),
            id_list
        )
    pool.join()
    pool.close()


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
api.add_command(set_token, 'set_token')
