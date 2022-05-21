import shutil
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Iterator, Iterable

from pkm.api.dependencies.dependency import Dependency
from pkm.api.distributions.distinfo import DistInfo, RecordsFileConfiguration
from pkm.api.distributions.pth_link import PthLink
from pkm.api.environments.environment import Environment
from pkm.api.packages.package import Package, PackageDescriptor
from pkm.api.packages.package_installation import PackageInstallationTarget
from pkm.api.packages.package_metadata import PackageMetadata
from pkm.api.packages.site_packages import InstalledPackage
from pkm.api.repositories.repository import AbstractRepository, Repository
from pkm.distributions.executables import Executables
from pkm.utils.commons import NoSuchElementException
from pkm.utils.files import CopyTransaction, is_empty_directory, is_relative_to
from pkm.utils.iterators import first_or_none


class SharedPackagesRepository(AbstractRepository):

    def __init__(self, workspace: Path, base_repository: Repository):
        super().__init__("shared")
        self._workspace = workspace
        self._base_repo = base_repository

    def remove_unused_packages(self, package_users: Iterator[Environment]):
        used_packages: Set[str] = set()
        for package_user in package_users:
            for used_package in package_user.site_packages.installed_packages():
                if (shared_marker := used_package.dist_info.path / "SHARED").exists():
                    used_packages.add(shared_marker.read_text())

        for package_dir in self._workspace.iterdir():
            if not package_dir.is_dir():
                continue

            for version_dir in package_dir.iterdir():
                if not version_dir.is_dir():
                    continue

                for shared_dir in version_dir.iterdir():
                    if not shared_dir.is_dir():
                        continue

                    if str(shared_dir.absolute()) not in used_packages:
                        shutil.rmtree(shared_dir)

                if is_empty_directory(version_dir):
                    version_dir.rmdir()

            if is_empty_directory(package_dir):
                package_dir.rmdir()

    def _do_match(self, dependency: Dependency, env: Environment) -> List[Package]:
        packages_dir = self._workspace / dependency.package_name
        packages = self._base_repo.match(dependency, env)
        return [
            _SharedPackage(p, packages_dir / str(p.version))
            for p in packages
        ]

    def _sort_by_priority(self, dependency: Dependency, packages: List[Package]) -> List[Package]:
        def key(p: Package):
            return 0 if isinstance(p, _SharedPackage) else 1

        packages.sort(key=key)
        return packages

    def accepted_url_protocols(self) -> Iterable[str]:
        return self._base_repo.accepted_url_protocols()

    def accept_non_url_packages(self) -> bool:
        return self._base_repo.accept_non_url_packages()


@dataclass
class _SharedPackageArtifact:
    path: Path
    metadata: PackageMetadata
    compatibility_tags: str


class _SharedPackage(Package):

    def __init__(self, package: Package, shared_path: Path):
        self._package = package
        self._shared_path = shared_path

        if shared_path.exists():
            self._artifacts = [
                _SharedPackageArtifact(artifact, PackageMetadata.load(artifact / "dist-info/METADATA"), artifact.name)
                for artifact in shared_path.iterdir()
            ]
        else:
            self._artifacts = []

    @property
    def descriptor(self) -> PackageDescriptor:
        return self._package.descriptor

    def _shared_artifact_for(self, env: Environment) -> Optional[_SharedPackageArtifact]:
        try:
            return max(
                ((a, s) for a in self._artifacts
                 if (s := env.compatibility_tag_score(a.compatibility_tag)) is not None),
                key=lambda it: it[1]
            )[0]
        except ValueError:
            return None

    def dependencies(
            self, environment: "Environment",
            extras: Optional[List[str]] = None) -> List["Dependency"]:

        if artifact := self._shared_artifact_for(environment):
            deps = artifact.metadata.dependencies
        else:
            deps = self._package.dependencies(environment)

        return [d for d in deps if d.is_applicable_for(environment, extras)]

    def is_compatible_with(self, env: "Environment") -> bool:
        return self._package.is_compatible_with(env)

    def install_to(
            self, target: "PackageInstallationTarget", user_request: Optional["Dependency"] = None,
            editable: bool = False):
        if shared := self._shared_artifact_for(target.env):
            _link_shared(self.descriptor, shared, target)
        else:
            self._package.install_to(target, user_request, editable)
            if shared := _move_to_shared(self._package.descriptor, target, self._shared_path):
                _link_shared(self.descriptor, shared, target)


def _copy_records(root: Path, shared: Path, records: List[Path]) -> List[Path]:
    shared.mkdir(parents=True)
    records_left = []
    for record in records:
        if is_relative_to(record, root):  # the path may lead out of the required source
            shared_path = shared / record.relative_to(root)
            if record.is_dir():
                shared_path.mkdir(exist_ok=True, parents=True)
            elif record.exists():
                shared_path.parent.mkdir(exist_ok=True, parents=True)
                shutil.copy(record, shared_path)
        else:
            records_left.append(record)
    return records_left


def _move_to_shared(package: PackageDescriptor,
                    target: PackageInstallationTarget, shared_path: Path) -> Optional[_SharedPackageArtifact]:
    psname = (package.expected_src_package_name + "-").lower()

    for site in ('purelib', 'platlib'):
        dist_info_path = first_or_none(
            it for it in Path(getattr(target, site)).glob("*.dist-info") if it.name.lower().startswith(psname))

        if dist_info_path:
            break
    else:
        raise NoSuchElementException(f"package: {package} is reported as installed but could not be find inside venv")

    dist_info = DistInfo.load(dist_info_path)

    iinfo = dist_info.load_installation_info()
    if iinfo.compatibility_tag:
        compatibility_tags = iinfo.compatibility_tag
        shared_target = shared_path / compatibility_tags
    else:
        return None  # TODO should probably notify the user that sharing is impossible for this package

    records = list(dist_info.installed_files())

    # filter dist info records:
    records = [
        r for r in records
        if not is_relative_to(r, dist_info.path)]

    # copy site
    shared_purelib = shared_target / site
    records = _copy_records(dist_info.path.parent, shared_purelib, records)

    # copy scripts
    script_entrypoints = {e.name for e in dist_info.load_entrypoints_cfg().entrypoints if e.is_script()}
    bin_path = Path(target.scripts)
    shared_bin = shared_target / "bin"

    # filter script entrypoints - they should be re-generated
    records = [r for r in records if not is_relative_to(r, bin_path) or r.stem not in script_entrypoints]
    records = _copy_records(bin_path, shared_bin, records)

    # copy dist-info
    shutil.copytree(dist_info.path, shared_target / 'dist-info')

    if records:
        warnings.warn(f"{len(records)} unsharable records found in package: {package.name} {package.version}: "
                      f"{', '.join(str(r) for r in records)}")

    # uninstall the original package
    InstalledPackage(dist_info).uninstall()

    return _SharedPackageArtifact(shared_target, dist_info.load_metadata_cfg(), shared_target.name)


def _link_shared(package: PackageDescriptor, shared: _SharedPackageArtifact, target: PackageInstallationTarget):
    with CopyTransaction() as ct:

        package_prefix = f"{package.expected_src_package_name}-{package.version}"

        site_name = "purelib" if (shared.path / "purelib").exists() else "platlib"
        site_path = Path(getattr(target, site_name))

        # first link the site data
        purelib_link = PthLink(site_path / f"{package_prefix}.pth", [shared.path / site_name])
        purelib_link.save()
        ct.touch(purelib_link.path)

        # now create all script entrypoints
        shared_distinfo = DistInfo.load(shared.path / "dist-info", non_standard_name_ok=True)
        bin_dir = Path(target.scripts)
        for entrypoint in shared_distinfo.load_entrypoints_cfg().entrypoints:
            if entrypoint.is_script():
                ct.touch(Executables.generate_for_entrypoint(target.env, entrypoint, bin_dir))

        # then, patch non entrypoint scripts
        for script in (shared.path / 'bin').iterdir():
            target_script = bin_dir / script.name
            Executables.patch_shabang_for_interpreter(script, target_script, target.env.interpreter_path)
            ct.touch(target_script)

        # we are almost done, copy dist-info
        distinfo_path = site_path / f"{package_prefix}.dist-info"
        ct.copy_tree(shared_distinfo.path, distinfo_path, lambda it: it.name != "RECORD")
        shared_marker = (distinfo_path / "SHARED")
        shared_marker.write_text(str(shared.path.absolute()))
        ct.touch(shared_marker)

        # and finally, sign the installation
        record_path = distinfo_path / "RECORD"
        RecordsFileConfiguration.load(record_path).sign_files(ct.copied_files, site_path).save()
