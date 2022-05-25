import click
from typing import Iterable, Tuple, Optional
from ubai_client.apis import SearchApi
from ubai_client.models import ArtifactStorage
from time import sleep
from utf_queue_client.scripts import setup_telemetry


@click.command()
@click.option("--name", default=None, help="artifact name")
@click.option("--extension", default=None, help="artifact extension, e.g. '.bin'")
@click.option("--metadata", multiple=True, type=(str, str))
@click.option(
    "--retries", default=3, help="number of retries (in case of network-related issues)"
)
def cli_entrypoint(
    name: Optional[str],
    extension: Optional[str],
    metadata: Iterable[Tuple[str, str]],
    retries: int,
):
    search_results = cli(name, extension, metadata, retries)
    for result in search_results:
        print(result)


def cli(
    name: Optional[str],
    extension: Optional[str],
    metadata: Iterable[Tuple[str, str]],
    retries: int = 3,
):
    with setup_telemetry():
        search_api = SearchApi()
        metadata_dict = {}
        for key, value in metadata:
            metadata_dict[key] = value
        if len(metadata_dict) == 0 and name is None and extension is None:
            raise RuntimeError("Must specify at least one search criterion")
        search_opts = ArtifactStorage(metadata=metadata_dict)
        if name is not None:
            search_opts.name = name
        if extension is not None:
            search_opts.extension = extension

        total_attempts = retries + 1
        for try_index in range(total_attempts):
            try:
                search_results = search_api.find_all_artifacts(search_opts)
                return [result.id for result in search_results]
            except Exception:
                if (try_index + 1) >= total_attempts:
                    raise
                sleep(10)


if __name__ == "__main__":
    cli_entrypoint()
