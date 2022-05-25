import os

from utf_queue_client.clients.ubai_artifact_upload_request_producer import (
    UbaiArtifactUploadRequestProducer,
)
from urllib import parse
import click
from typing import Iterable, Tuple
from time import sleep
from utf_queue_client.scripts import setup_telemetry
from retry import retry


@click.command()
@click.option(
    "--file-path",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Path to file to upload",
)
@click.option("--metadata", multiple=True, type=(str, str))
@click.option(
    "--username",
    envvar="UTF_QUEUE_USERNAME",
    help="UTF queue username",
)
@click.option(
    "--password",
    envvar="UTF_QUEUE_PASSWORD",
    help="UTF queue password",
)
@click.option(
    "--client-id", type=str, default="Unknown Client", help="Optional client identifier"
)
@click.option(
    "--retries", default=6, help="number of retries (in case of network-related issues)"
)
@click.option("--queue/--no-queue", default=False)
def cli_entrypoint(
    file_path: str,
    metadata: Iterable[Tuple[str, str]],
    username: str,
    password: str,
    client_id: str,
    retries: int,
    queue: bool,
):
    cli(file_path, metadata, username, password, client_id, retries, queue)


def cli(
    file_path: str,
    metadata: Iterable[Tuple[str, str]],
    username: str,
    password: str,
    client_id: str,
    retries: int = 6,
    queue: bool = False,
):
    with setup_telemetry():
        url = ""
        if queue:
            if username is None or password is None:
                raise RuntimeError(
                    "username or password must be provided if using queue"
                )
            hostname = os.environ.get(
                "UTF_QUEUE_HOSTNAME", "utf-queue-central.silabs.net"
            )
            scheme = os.environ.get("UTF_QUEUE_SCHEME", "amqps")
            port = os.environ.get("UTF_QUEUE_PORT", "443")
            virtual_host = os.environ.get("UTF_QUEUE_VIRTUAL_HOST", "%2f")
            url = f"{scheme}://{username}:{parse.quote(password)}@{hostname}:{port}/{virtual_host}"

        metadata_dict = {}
        for key, value in metadata:
            metadata_dict[key] = value

        @retry(Exception, delay=3, backoff=2, max_delay=12, tries=retries + 1)
        def retry_wrapper():
            if queue:
                upload_artifact_through_queue(url, client_id, file_path, metadata_dict)
            else:
                upload_artifact_direct(file_path, metadata_dict)

        retry_wrapper()
        if not queue:
            # workaround to reduce load
            sleep(2)


def upload_artifact_through_queue(url, client_id, file_path, metadata_dict):
    client = UbaiArtifactUploadRequestProducer(url, client_id)
    client.upload_artifact(file_path, metadata=metadata_dict)


def upload_artifact_direct(file_path, metadata_dict):
    (
        name,
        extension,
        contents,
        base64_content,
    ) = UbaiArtifactUploadRequestProducer.extract_payload(file_path)
    UbaiArtifactUploadRequestProducer.upload_artifact_direct(
        name, extension, base64_content, metadata_dict
    )


if __name__ == "__main__":
    cli_entrypoint()
