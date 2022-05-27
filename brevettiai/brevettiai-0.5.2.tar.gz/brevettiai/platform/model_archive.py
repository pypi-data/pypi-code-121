import hashlib
import logging
import os
import re
import tarfile
from tarfile import ReadError

from dataclasses import dataclass
from io import BytesIO
from typing import Dict

from pydantic import Field

from brevettiai.model.metadata import ModelMetadata
from brevettiai.platform import Job
from brevettiai.utils.model_version import get_model_version

log = logging.getLogger(__name__)


@dataclass
class ModelArchiveAsset:
    """
    Data holder for file names and hashes of assets in model archive
    """
    file: str
    hash: str


class ModelArchiveMetadata(ModelMetadata):
    """
    Metadata for model archives
    adding an assets field for users of the archive to check if it contains what is needed
    """
    assets: Dict[str, ModelArchiveAsset] = Field(default_factory=dict,
                                                 description="Key value pairs of name and path to asset")


class ModelArchive:
    """
    ModelArchive Wrapper class, to help create archives with assets and metadata
    """
    METADATA_URI = "metadata.json"
    """location of metadata file"""

    def __init__(self, path=None, metadata: ModelMetadata = None, job: Job = None):
        """
        Initialize model archive.
        Can use job or metadata as source, if neither are given metadata is loaded from current archive

        Notes:
            * Use the context manager to write assets.
            * When entering the write context previously existing assets are not copied to the new archive

        Usage:
            in Job.run:

            ```python
            archive = ModelArchive(job=self)
            with archive.open_write() as writer:
                writer.add_asset(name="onnx", arcname="model.onnx", file=self.temp_path("model.onnx"))

            with archive.open_read() as reader:
                with reader.get_asset("onnx") as fp:
                    data = fp.read()

            ...
            return archive.upload(self)
            ```

        Args:
            path: location of archive (Must end with tar.gz), if job given and path is None f"{job.name}.tar.gz" is chosen
            metadata: optional ModelMetadata
            job: optional job to gather metadata from if metadata keyword is missing
        """
        self.path = path or job.temp_path(f"{re.sub('[^-a-zA-Z0-9_.()]+', '_', job.name)}.tar.gz".lower())
        try:
            if metadata is not None:
                self.metadata = ModelArchiveMetadata.parse_obj(metadata)
            elif job is not None:
                self.metadata = ModelArchiveMetadata.parse_obj(job.get_metadata())
                if os.path.isfile(self.path):
                    with tarfile.open(self.path, "r:gz") as arc:
                        fp = arc.extractfile(ModelArchive.METADATA_URI)
                        self.metadata.assets = ModelArchiveMetadata.parse_raw(fp.read()).assets
            else:
                if not os.path.isfile(self.path):
                    raise TypeError("Model archive needs 'metadata' to create archive")
                with tarfile.open(self.path, "r:gz") as arc:
                    fp = arc.extractfile(ModelArchive.METADATA_URI)
                    self.metadata = ModelArchiveMetadata.parse_raw(fp.read())
        except tarfile.TarError as ex:
            raise IOError("Error opening archive") from ex

        self._archive = None

    def _write_metadata(self, archive):
        buffer = BytesIO()
        buffer.write(self.metadata.json(indent=2).encode("utf-8"))
        info = tarfile.TarInfo(name=ModelArchive.METADATA_URI)
        info.size = buffer.tell()
        buffer.seek(0)
        archive.addfile(tarinfo=info, fileobj=buffer)

    def add_asset(self, name, arcname, file) -> ModelArchiveAsset:
        """
        Add an asset to the archive

        Args:
            name: name of asset
            arcname: name of file location in archive to save asset
            file: Path to asset to add to archive

        Returns:
            ModelArchiveAsset
        """
        if self._archive is None:
            raise IOError("Archive not open. use: 'with archive.writer() as writer:'")
        if self._archive.mode != "w":
            raise IOError("Archive not in write mode. use: 'with archive.writer() as writer:'")

        # Normalize path
        arcname = os.path.normpath(arcname).replace("\\", "/")

        # Create asset
        asset = ModelArchiveAsset(file=arcname, hash=self._get_hash(file))
        self._archive.add(name=file, arcname=arcname)
        self.metadata.assets[name] = asset
        return asset

    def open_read(self):
        if self._archive is None:
            try:
                self._archive = tarfile.open(self.path, f"r:gz")
            except tarfile.TarError as ex:
                raise IOError("Error opening archive") from ex
        if self._archive.mode != "r":
            raise IOError("Archive already opened in write mode")
        return self

    def open_write(self):
        if self._archive is None:
            try:
                self._archive = tarfile.open(self.path, f"w:gz")
            except tarfile.TarError as ex:
                raise IOError("Error opening archive") from ex
            self.metadata.assets.clear()
        if self._archive.mode != "w":
            raise IOError("Archive already opened in read mode")
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._archive.mode == "w":
            self._write_metadata(self._archive)
        self._archive.close()
        self._archive = None

    def get_asset(self, name):
        if self._archive is None:
            raise IOError("Archive not open. use: 'with archive.reader() as reader:'")
        if self._archive.mode != "r":
            raise IOError("Archive not in read mode. use: 'with archive.reader() as reader:'")
        try:
            asset = self.metadata.assets[name]
        except KeyError as ex:
            raise KeyError(f"Asset '{name} not in archive'") from ex

        try:
            return self._archive.extractfile(asset.file)
        except tarfile.TarError as ex:
            raise IOError("Error extracting asset from archive") from ex

    @staticmethod
    def _get_hash(filename):
        sha256 = hashlib.sha256()
        with open(filename, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256.update(byte_block)
        return f"sha256:{sha256.hexdigest()}"

    @property
    def versioned_name(self) -> str:
        """
        Get a versioned name according to the specification name.tar.gz -> name.version.tar.gz
        where the version is generated by `get_model_version`

        Returns: versioned file name

        """
        if not os.path.isfile(self.path):
            raise IOError("Archive does not exist, use 'with' keyword build archive")
        if self._archive is not None and not self._archive.closed:
            raise IOError("Archive file not closed")

        archive_name = os.path.basename(self.path)
        split_name = archive_name.rsplit(".", 2)
        split_name.insert(1, str(get_model_version(self.path)))
        return ".".join(split_name)

    @classmethod
    def from_job(cls, job, tmpdir):
        if not job.model_path:
            raise AttributeError("Job does not contain a ModelArchive")
        model_archive_path = job.io.path.join(job.job_dir, job.model_path)
        tmp_archive_path = os.path.join(tmpdir, os.path.basename(model_archive_path))
        job.io.copy(model_archive_path, tmp_archive_path)
        return cls(path=tmp_archive_path)
