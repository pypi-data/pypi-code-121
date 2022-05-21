import hashlib
import shutil
from pathlib import Path
from typing import Any

import pkm.pep517_builders.external_builders as ext_build
from pkm.api.distributions.source_distribution import SourceDistribution
from pkm.api.distributions.wheel_distribution import WheelDistribution
from pkm.api.environments.environment import Environment
from pkm.api.packages.package import PackageDescriptor
from pkm.api.packages.package_installation import PackageInstallationTarget
from pkm.api.packages.package_metadata import PackageMetadata
from pkm.api.projects.project import Project
from pkm.pep517_builders.external_builders import BuildError
from pkm.utils.archives import extract_archive
from pkm.utils.files import temp_dir
from pkm.utils.hashes import stream
from pkm.utils.iterators import single_or, single_or_raise

_normalize = PackageDescriptor.normalize_src_package_name


class SourceBuildCache:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        workspace.mkdir(parents=True, exist_ok=True)

    def _version_dir(self, package: PackageDescriptor) -> Path:
        return self.workspace / package.name / _normalize(str(package.version))

    def get_or_build_wheel(self, target: PackageInstallationTarget, dist: SourceDistribution) -> Path:
        return self._get_or_build(target, dist, 'wheel')

    def get_or_build_meta(self, env: Environment, dist: SourceDistribution) -> PackageMetadata:
        return self._get_or_build(env.installation_target, dist, 'metadata')

    def _get_or_build(self, target: PackageInstallationTarget, dist: SourceDistribution, artifact: str) -> Any:

        base_cache_dir = self.workspace / _normalize(dist.owner_package.name) / \
                         _normalize(str(dist.owner_package.version)) / \
                         target.env.markers_hash

        dist_hash = hashlib.blake2s()
        stream(dist_hash, dist.archive)
        dist_hash_value = dist_hash.hexdigest()
        metadata = artifact == 'metadata'
        cache_dir = base_cache_dir / dist_hash_value
        metadata_file = cache_dir / "METADATA"

        if metadata_file.exists():
            if metadata:
                return PackageMetadata.load(metadata_file)
            if wheel := single_or(cache_dir.glob("*.whl"), None):
                return wheel

        if base_cache_dir.exists():
            shutil.rmtree(base_cache_dir)

        with temp_dir() as tdir:
            extract_archive(dist.archive, tdir)
            sdir = single_or_raise(tdir.iterdir())
            project = Project.load(sdir, dist.owner_package)
            odir = tdir / 'output'

            try:
                output = ext_build.build_wheel(
                    project, odir, only_meta=metadata, editable=False, target_env=target.env)
            except BuildError as e:
                if not metadata or not e.missing_hook:
                    raise
                output = ext_build.build_wheel(
                    project, odir, only_meta=False, target_env=target.env)

            if output.is_dir():  # metadata
                wheel_metadata_path = output / 'METADATA'
                if not wheel_metadata_path.exists():
                    raise BuildError("build backend did not create a wheel METADATA file")

                cache_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy(wheel_metadata_path, metadata_file)
                return PackageMetadata.load(wheel_metadata_path)
            else:
                if not metadata_file.exists():
                    metadata = WheelDistribution(dist.owner_package, output).extract_metadata()
                    metadata.save_to(metadata_file)

                cached_output = cache_dir / output.name
                cache_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(output, cached_output)
                return cached_output
