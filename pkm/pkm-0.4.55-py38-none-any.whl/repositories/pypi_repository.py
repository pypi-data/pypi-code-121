import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from pkm.api.dependencies.dependency import Dependency
from pkm.api.environments.environment import Environment
from pkm.api.packages.package import Package, PackageDescriptor
from pkm.api.packages.package_metadata import PackageMetadata
from pkm.api.packages.standard_package import AbstractPackage, PackageArtifact
from pkm.api.pkm import pkm
from pkm.api.repositories.repository import AbstractRepository, RepositoryBuilder, Repository
from pkm.api.repositories.repository import RepositoryPublisher
from pkm.api.versions.version import Version
from pkm.api.versions.version_specifiers import VersionSpecifier
from pkm.utils.commons import NoSuchElementException
from pkm.utils.http.auth import BasicAuthentication
from pkm.utils.http.cache_directive import CacheDirective
from pkm.utils.http.http_client import HttpClient, HttpException
from pkm.utils.http.mfd_payload import FormField, MultipartFormDataPayload
from pkm.utils.io_streams import chunks
from pkm.utils.properties import cached_property


class PyPiRepository(AbstractRepository):

    def __init__(self, name: str, fetch_url: str, publish_url: Optional[str]):
        super().__init__(name)
        self._http = pkm.httpclient
        self._fetch_url = fetch_url
        self._publish_url = publish_url

    @cached_property
    def publisher(self) -> Optional["RepositoryPublisher"]:
        if self._publish_url:
            return PyPiPublisher(self.name, self._http, self._publish_url)
        return None

    def _do_match(self, dependency: Dependency, env: Environment) -> List[Package]:
        try:
            json: Dict[str, Any] = self._http \
                .fetch_resource(f'{self._fetch_url}/{dependency.package_name}/json',
                                cache=CacheDirective.ask_for_update(),
                                resource_name=f"matching packages for {dependency}") \
                .read_data_as_json()
        except HttpException as e:
            raise NoSuchElementException(
                f"package: '{dependency.package_name}' could not be retrieved from repository: '{self.name}'") from e

        package_info: Dict[str, Any] = {k.replace('_', '-').title(): v for k, v in json['info'].items()}

        packages: List[PypiPackage] = []
        releases: Dict[str, Any] = json['releases']
        for version_str, release in releases.items():

            relevant_artifacts = []
            for a in release:
                if not a.get('yanked') and a.get("packagetype") in ("sdist", "bdist_wheel"):
                    if sa := _create_artifact_from_pypi_release(a):
                        relevant_artifacts.append(sa)

            if relevant_artifacts:
                version = Version.parse(version_str)
                if dependency.version_spec.allows_version(version):
                    packages.append(PypiPackage(
                        PackageDescriptor(dependency.package_name, version),
                        relevant_artifacts, self, PackageMetadata(path=None, data=package_info)
                    ))

        return packages


# noinspection PyProtectedMember
class PypiPackage(AbstractPackage):

    def __init__(self, descriptor: PackageDescriptor, artifacts: List[PackageArtifact], repo: PyPiRepository,
                 metadata: PackageMetadata):

        super().__init__(descriptor, artifacts, metadata)
        self._repo = repo

    def _retrieve_artifact(self, artifact: PackageArtifact) -> Path:
        url = artifact.other_info.get('url')
        if not url:
            raise KeyError(f'could not find url in given artifact info: {artifact}')

        resource = self._repo._http.fetch_resource(url, resource_name=f"{self.name} {self.version}")
        if not resource:
            raise FileNotFoundError(f'cannot find requested artifact: {artifact.file_name}')

        return resource.data

    def _unfiltered_dependencies(self, environment: Environment) -> List["Dependency"]:
        json: Dict[str, Any] = self._repo._http \
            .fetch_resource(f'{self._repo._fetch_url}/{self.name}/{self.version}/json',
                            resource_name=f"metadata for {self.name} {self.version}") \
            .read_data_as_json()

        requires_dist = json['info'].get('requires_dist')
        if requires_dist is None:
            return super(PypiPackage, self)._unfiltered_dependencies(environment)

        return [Dependency.parse(dstr) for dstr in requires_dist]


def _create_artifact_from_pypi_release(release: Dict[str, Any]) -> Optional[PackageArtifact]:
    requires_python = release.get('requires_python')

    file_name: str = release.get('filename')
    if not file_name:
        return None

    return PackageArtifact(
        file_name, VersionSpecifier.parse(requires_python) if requires_python else None, release
    )


# https://warehouse.pypa.io/api-reference/legacy.html
class PyPiPublisher(RepositoryPublisher):

    def __init__(self, repo_name: str, http: HttpClient, publish_url: str):
        super().__init__(repo_name)
        self._http = http
        self._publish_url = publish_url

    def publish(self, auth_args: Dict[str, str], package_meta: PackageMetadata, distribution: Path):
        print(f"uploading distribution: {distribution}")

        data = {k.replace('-', '_').lower(): v for k, v in package_meta.items()}
        file_type = 'bdist_wheel' if distribution.suffix == '.whl' else 'sdist'
        py_version = distribution.name.split("-")[2] if distribution.suffix == '.whl' else 'source'

        md5, sha256, blake2 = hashlib.md5(), hashlib.sha256(), hashlib.blake2b(digest_size=256 // 8)
        with distribution.open('rb') as d_fd:
            for chunk in chunks(d_fd):
                md5.update(chunk)
                sha256.update(chunk)
                blake2.update(chunk)

        data.update({
            'filetype': file_type,
            'pyversion': py_version,
            'md5_digest': md5.hexdigest(),
            'sha256_digest': sha256.hexdigest(),
            'blake2_256_digest': blake2.hexdigest(),
            ':action': 'file_upload',
            'protocol_version': '1'
        })

        fields: List[FormField] = []
        for k, v in data.items():
            if isinstance(v, (Tuple, List)):
                for iv in v:
                    fields.append(FormField(k, iv))
            else:
                fields.append(FormField(k, v))

        with distribution.open('rb') as d_fd:
            fields.append(FormField('content', d_fd, filename=distribution.name)
                          .set_content_type("application/octet-stream"))

            payload = MultipartFormDataPayload(fields=fields)
            headers = dict([
                BasicAuthentication(**auth_args).as_header(),
                ("Content-Type", payload.content_type()),
            ])

            with self._http.post(f"{self._publish_url}/", payload, headers=headers,
                                 max_redirects=0) as response:
                if response.status != 200:
                    content = response.read()
                    raise HttpException(f"publish failed, server responded with {response.status}, {content}")


class PypiRepositoryBuilder(RepositoryBuilder):

    def __init__(self):
        super().__init__('pypi')

    def build(self, name: str, args: Dict[str, str]) -> Repository:
        url = self._arg(args, 'url', required=True)

        if url == 'main':
            fetch_url = "https://pypi.org/pypi"
            publish_url = "https://upload.pypi.org/legacy"
        elif url == 'test':
            fetch_url = "https://test.pypi.org/pypi"
            publish_url = "https://test.pypi.org/legacy"
        else:
            fetch_url = url.rstrip('/')
            publish_url = self._arg(args, 'publish-url')

        return PyPiRepository(name, fetch_url, publish_url)
