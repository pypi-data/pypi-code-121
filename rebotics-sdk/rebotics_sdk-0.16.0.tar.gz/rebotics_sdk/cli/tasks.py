import os

import click

from rebotics_sdk.providers import ProviderHTTPClientException


def task_create_processing_action_for_image(ctx, store_id, image_path):
    under_images_folder = os.path.join(os.getcwd(), 'images', image_path)
    cwd_filepath = os.path.join(os.getcwd(), image_path)
    if os.path.exists(under_images_folder):
        filepath = under_images_folder
    elif os.path.exists(cwd_filepath):
        filepath = cwd_filepath
    else:
        if ctx.verbose:
            click.echo('File does not exist {}'.format(image_path))
        return None

    with open(filepath, 'rb') as file_io:
        processing_input_dict = ctx.provider.processing_upload(store_id, file_io)
        if ctx.verbose:
            click.echo('File uploaded with id {}'.format(processing_input_dict['id']))

    processing_action_dict = ctx.provider.create_processing_action(
        store_id,
        [processing_input_dict['id']],
    )
    if ctx.verbose:
        click.echo('Processing action created with id {}'.format(processing_action_dict['id']))

    return processing_action_dict['id']


def upload_preview_task(d):
    ctx = d['ctx']
    images_path = d['images_path']
    upc = d['upc']
    delete = d['delete']

    if delete:
        try:
            response = ctx.provider.delete_product_previews(upc)
            click.echo('Deleted %s previews for product %s' % (response['deleted'], upc,), err=True)
        except ProviderHTTPClientException:
            click.echo('Product with UPC %s does not exists' % upc, err=True)

    for image_path in images_path:
        with open(image_path, 'rb') as image:
            try:
                ctx.provider.upload_product_preview(upc, image)
            except ProviderHTTPClientException as e:
                click.echo("xxx Failed to send image: %s" % image_path)
                click.echo(str(e), err=True)
            click.echo('<< Uploaded product preview for %s from %s' % (upc, image_path), err=True)


def task_download_processing_action(ctx, processing_action_id):
    try:
        processing_action_id = int(processing_action_id)
    except (ValueError, TypeError):
        processing_action_id = None

    if processing_action_id:
        if ctx.verbose:
            click.echo('Downloading processing action {}'.format(processing_action_id), err=True)
        try:
            return ctx.provider.processing_action_detail(processing_action_id)
        except ProviderHTTPClientException:
            return None


def task_recalculate_processing(d):
    ctx = d['ctx']
    provider = ctx.provider
    response = provider.recalculate(d['id'])
    if ctx.verbose:
        click.echo(response)
        click.echo(response['id'])
    return response


def task_cancel_processing(d):
    ctx = d['ctx']
    provider = ctx.provider
    response = provider.cancel(d['id'])
    if ctx.verbose:
        click.echo(response)
        click.echo(response['id'])
    return response


def task_requeue_processing(d):
    ctx = d['ctx']
    provider = ctx.provider
    response = provider.requeue(d['id'], d['requeue_type'])
    if ctx.verbose:
        click.echo(response)
        click.echo(response['id'])
    return response
