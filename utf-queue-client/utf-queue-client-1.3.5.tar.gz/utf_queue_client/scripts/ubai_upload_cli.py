import os

from utf_queue_client.clients.ubai_artifact_upload_request_producer import (
    UbaiArtifactUploadRequestProducer,
)
from urllib import parse
import click
from typing import Iterable, Tuple
from time import sleep
from utf_queue_client.scripts import setup_telemetry


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
    "--retries", default=3, help="number of retries (in case of network-related issues)"
)
def cli_entrypoint(
    file_path: str,
    metadata: Iterable[Tuple[str, str]],
    username: str,
    password: str,
    client_id: str,
    retries: int,
):
    cli(file_path, metadata, username, password, client_id, retries)


def cli(
    file_path: str,
    metadata: Iterable[Tuple[str, str]],
    username: str,
    password: str,
    client_id: str,
    retries: int = 3,
):
    with setup_telemetry():
        if username is None or password is None:
            raise RuntimeError("username or password must be provided")
        hostname = os.environ.get("UTF_QUEUE_HOSTNAME", "utf-queue-central.silabs.net")
        scheme = os.environ.get("UTF_QUEUE_SCHEME", "amqps")
        port = os.environ.get("UTF_QUEUE_PORT", "443")
        virtual_host = os.environ.get("UTF_QUEUE_VIRTUAL_HOST", "%2f")
        url = f"{scheme}://{username}:{parse.quote(password)}@{hostname}:{port}/{virtual_host}"

        metadata_dict = {}
        for key, value in metadata:
            metadata_dict[key] = value

        total_attempts = retries + 1
        for try_index in range(total_attempts):
            try:
                if try_index > 0:
                    upload_artifact_direct(file_path, metadata_dict)
                else:
                    upload_artifact_through_queue(
                        url, client_id, file_path, metadata_dict
                    )
                break
            except Exception:
                if (try_index + 1) >= total_attempts:
                    raise
                sleep(10)


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
