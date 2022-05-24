from dataclasses import dataclass
from os.path import split
from pathlib import Path
from typing import Iterator, Optional, Union, List
from re import compile

# use simple import to avoid 'partially initialized module' with experiments + runs
import grid.sdk.experiments
import grid.sdk.runs
from grid.cli.utilities import is_experiment
from grid.sdk.utils.downloader import DownloadableObject, Downloader


@dataclass(frozen=True)
class Artifact:
    url: str
    filename: str
    experiment_name: str
    run_name: str

    def to_downloadable_object(self) -> DownloadableObject:
        """Returns an object that can be used by grid.sdk.utils.downloader.Downloader
        """
        path, filename = split(self.filename)
        return DownloadableObject(
            url=self.url,
            download_path=path,
            filename=filename,
        )

    def download(self, destination: str = "./grid_artifacts"):
        """Downloads the artifact to the filesystem.

        It may be easier to use `experiment.download_artifacts()` or
        `run.download_artifacts()` depending on your use case.

        Parameters
        ----------
        destination : str, optional
            Path to place the download, by default "./grid_artifacts"
        """
        Downloader.single_file_download(
            obj=self.to_downloadable_object(),
            dest=destination,
        )


def _filter_artifacts(artifact_regex: str, artifacts: List[Artifact]) -> List[Artifact]:
    """Extracted from `list_artifacts` for easier unit testing
    """
    regex = compile(artifact_regex)
    filtered = filter(
        lambda artifact: regex.search(artifact.filename),
        artifacts,
    )
    return list(filtered)


def list_artifacts(run_or_experiment_name: str,
                   cluster_id: Optional[str] = None,
                   artifact_regex: str = "") -> List[Artifact]:
    """Lists all artifacts for all experiments created by the user.

    Parameters
    ----------
    run_or_experiment_name : str
        Returns the artifacts for this run / experiment.
    cluster_id : Optional[str], optional
        The id of the cluster to search runs for. If None, the default cluster (as listed
        in settings.json) is used.
    artifact_regex : str, optional
        If provided, only return artifacts which match this regex (applied to artifact's filename)

    Returns
    -------
    List[Artifact]
    """

    # get the artifacts from the appropriate source
    artifacts: Iterator[Artifact]
    if is_experiment(run_or_experiment_name):
        artifacts = grid.sdk.experiments.Experiment(name=run_or_experiment_name, cluster_id=cluster_id).artifacts
    else:
        artifacts = grid.sdk.runs.Run(name=run_or_experiment_name, cluster_id=cluster_id).artifacts

    # filter artifacts if necessary
    return _filter_artifacts(artifact_regex, artifacts)


def download_artifacts(artifacts: Iterator[Artifact], destination: Union[str, Path] = "./grid_artifacts"):
    """Download a list of artifacts in bulk

    Parameters
    ----------
    artifacts : Iterator[Artifact]
        The list of artifacts to download
    destination : Union[str, Path], optional
        Path to download artifacts, by default "./grid_artifacts"
    """
    Downloader.multi_file_download(
        destination=destination,
        downloadable_objects=(a.to_downloadable_object() for a in artifacts),
        description="artifacts downloaded",
        unit="artifact",
    )
