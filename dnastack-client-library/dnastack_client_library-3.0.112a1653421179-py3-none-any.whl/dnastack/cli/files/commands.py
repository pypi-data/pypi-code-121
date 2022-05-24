import os
from typing import List

import click

from .local_client_repository import LocalClientRepository
from ..utils import handle_error_gracefully, allow_to_specify_endpoint


@click.group('files')
def drs_command_group():
    """ Interact with Data Repository Service """


@drs_command_group.command("download")
@click.argument("urls", required=False, nargs=-1)
@click.option("-o", "--output-dir", required=False, default=os.getcwd(), show_default=True)
@click.option("-i", "--input-file", required=False, default=None)
@click.option("-q", "--quiet", is_flag=True, required=False, default=False)
@allow_to_specify_endpoint
@handle_error_gracefully
def download(endpoint_id: str,
             endpoint_url: str,
             urls: List[str],
             output_dir: str = os.getcwd(),
             input_file: str = None,
             quiet: bool = False):
    download_urls = []

    if len(urls) > 0:
        download_urls = list(urls)
    elif input_file:
        with open(input_file, "r") as infile:
            download_urls = filter(None, infile.read().split("\n"))  # need to filter out invalid values
    else:
        if not quiet:
            click.echo("Enter one or more URLs. Press q to quit")

        while True:
            try:
                url = click.prompt("", prompt_suffix="", type=str)
                url = url.strip()
                if url[0] == "q" or len(url) == 0:
                    break
            except click.Abort:
                break

            download_urls.append(url)

    LocalClientRepository.get(endpoint_id, endpoint_url) \
        .download_files(urls=download_urls,
                        output_dir=output_dir,
                        display_progress_bar=(not quiet))
