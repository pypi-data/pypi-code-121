import time
import typing as t
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from loguru import logger

from lifeomic_chatbot_tools.persistence.record_store.base import IRecord, IRecordStore


class IServiceVersionMetadata(IRecord, t.Protocol):
    name: str
    """The name of this version."""

    synced_at: float
    """Time the service version was most recently synced."""


TIServiceVersionMetadata = t.TypeVar("TIServiceVersionMetadata", bound=IServiceVersionMetadata)
TServiceVersionId = t.TypeVar("TServiceVersionId")


class IDatasetRecord(IRecord, t.Protocol):
    """Minimum required interface for a generic dataset object managed by an artifact manager."""

    agent_id: str
    updated_at: float

    @property
    def digest(self) -> str:
        """A hash of this record, which should be invariant to the `updated_at` attribute."""
        ...


TIDatasetRecord = t.TypeVar("TIDatasetRecord", bound=IDatasetRecord)
TDatasetId = t.TypeVar("TDatasetId")


class IArtifactRecord(IRecord, t.Protocol):
    """Minimum required interface for an artifact produced by a versioned dataset and a versioned model."""

    agent_id: str
    dataset_digest: str
    """The hash of the dataset that was used to produce this artifact."""

    service_version: str
    """The version of the model that produced this artifact."""

    updated_at: float


TIArtifactRecord = t.TypeVar("TIArtifactRecord", bound=IArtifactRecord)
TArtifactId = t.TypeVar("TArtifactId")


class BaseArtifactManager(
    t.Generic[TIArtifactRecord, TArtifactId, TIDatasetRecord, TDatasetId, TIServiceVersionMetadata, TServiceVersionId],
    ABC,
):
    """
    Clas which provides a simple API for creating, persisting, and managing artifacts produced by a versioned machine
    learning (ML) model. Each artifact is associated with an agent. An artifact is the deterministic product of a
    specific ML model version, and a specific version of a dataset.

    Attributes
    ----------
    get_version : callable
        A function which takes no arguments and returns the current model version when called.
    """

    def __init__(
        self,
        artifacts: IRecordStore[TArtifactId, TIArtifactRecord],
        datasets: IRecordStore[TDatasetId, TIDatasetRecord],
        versions: IRecordStore[TServiceVersionId, TIServiceVersionMetadata],
        version: t.Union[t.Callable[[], str], str],
        make_artifact_id: t.Callable[[str, str], TArtifactId],
        make_dataset_id: t.Callable[[str], TDatasetId],
        *,
        max_service_versions=5,
    ):
        """
        Parameters
        ----------
        artifacts : IRecordStoreStringId
            Data store used to store the artifacts.
        datasets : IRecordStoreStringId
            Data store used to store the datasets which are used to produce the artifacts.
        versions : IRecordStoreStringId
            Data store used to store metadata about each model version this manager interacts with.
        version : str or callable
            A function which takes no arguments, which should return the current model version when called. This is
            passed in as a function to support the use case where the underlying model version could change at any
            moment, for example because a new model was trained and deployed behind the scenes. If the model version
            does not change, a string can be passed in instead.
        make_artifact_id : callable
            A function which takes a service version and an agent id, and creates an ID for the artifact object created
            under that version, for that agent. We have an artifact's database ID be the deterministic product of the
            service version that created it, and the agent that the artifact is for. We do this because for a given
            service version, we only need to persist one artifact version per agent at a time.
        make_dataset_id : callable
            A function which accepts an agent id, and returns an id for that agent's dataset object, to be used to store
            the dataset in the dataset store.
        max_service_versions : int, optional
            The number of model versions (also called service versions) to track in the ``versions`` data store.
        """
        if isinstance(version, str):
            self.get_version = lambda: version
        else:
            self.get_version = version
        self._max_service_versions = max_service_versions
        self._artifacts = artifacts
        self._datasets = datasets
        self._versions = versions
        self._make_artifact_id = make_artifact_id
        self._make_dataset_id = make_dataset_id

    @abstractmethod
    def create_artifact_from_dataset(self, dataset: TIDatasetRecord) -> TIArtifactRecord:
        """
        Implementing subclasses should take ``dataset``, and the model associated with version ``self.get_version()``,
        and produce an artifact.
        """
        pass

    @abstractmethod
    def create_version_metadata(self, version: str, synced_at: float) -> TIServiceVersionMetadata:
        pass

    def delete_artifact(self, agent_id: str):
        """
        Deletes from the database a dataset and all artifacts associated with it, if they exist. Returns the number of
        total database records that were deleted.
        """
        num_deleted = int(self._datasets.delete(self._make_dataset_id(agent_id)))
        num_deleted += self._artifacts.delete_all(agent_id=agent_id)  # get rid of any old versions as well
        return num_deleted

    def save_artifact(self, artifact: TIArtifactRecord, dataset: TIDatasetRecord):
        """
        Serializes and saves the artifact. Also saves the dataset that was used to create the artifact, so this manager
        can recreate the artifact at any time if needed.
        """
        self._artifacts.save(artifact)
        self._datasets.save(dataset)

    def load_artifact(self, agent_id: str) -> TIArtifactRecord:
        """
        Load an agent's artifact from the database. If the agent's dataset exists but its artifact doesn't, then compute
        it, save it (so its available next time), and then return it.
        """
        dataset = self._datasets.get(self._make_dataset_id(agent_id))
        if dataset is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"no dataset exists for agent id {agent_id}; artifact cannot be retrieved or computed",
            )
        version = self.get_version()
        artifact = self._artifacts.get(self._make_artifact_id(version, agent_id))
        if artifact is not None and artifact.dataset_digest == dataset.digest:
            return artifact
        else:
            logger.info(
                f"artifact for agent {agent_id} does not exist for service version {version} and dataset "
                f"digest {dataset.digest}; creating it now"
            )
            # Artifact has not yet been created for this dataset version and service version.
            artifact = self.create_artifact_from_dataset(dataset)
            self.save_artifact(artifact, dataset)
            return artifact

    def sync(self) -> int:
        """
        Ensures this service version has its own artifact for all currently saved datasets. Returns the number of
        artifacts that had to be created for that to happen.
        """
        digest2agent = {dataset.digest: dataset.get_id() for dataset in self._datasets.get_all()}
        all_dataset_digests = set(digest2agent.keys())
        version = self.get_version()
        datasets_currently_indexed = {
            artifact.dataset_digest for artifact in self._artifacts.get_all(service_version=version)
        }
        datasets_to_index = all_dataset_digests - datasets_currently_indexed
        logger.info(
            f"creating artifact for {len(datasets_to_index)}/{len(all_dataset_digests)} "
            f"existing datasets for service version {version}"
        )
        for digest in datasets_to_index:
            dataset = self._datasets.get(digest2agent[digest])
            if dataset is None:
                raise AssertionError(
                    f"Expected dataset to exist for agent {digest2agent[digest]}. It existed just a little bit ago."
                )
            logger.info(f"creating artifact for dataset digest={digest} associated with agent {digest2agent[digest]}")
            artifact = self.create_artifact_from_dataset(dataset)
            self.save_artifact(artifact, dataset)

        metadata = self.create_version_metadata(version, time.time())
        self._versions.save(metadata)
        logger.info("service version sync utility finished successfully.")
        self._remove_old_service_versions()
        return len(datasets_to_index)

    def _remove_old_service_versions(self):
        """
        Removes all artifacts for any old service versions. We only keep data for the ``self._max_service_versions``
        most recent service versions. The old versions are the ones that have been synced least recently.
        """
        versions = list(self._versions.get_all())
        n_to_remove = len(versions) - self._max_service_versions
        if n_to_remove > 0:
            logger.info(f"removing data for {n_to_remove} old service versions")
            # Remove the oldest versions.
            versions_to_remove = sorted(versions, key=lambda v: v.synced_at)[:n_to_remove]
            for version in versions_to_remove:
                self._artifacts.delete_all(service_version=version.name)
                self._versions.delete(version.get_id())
