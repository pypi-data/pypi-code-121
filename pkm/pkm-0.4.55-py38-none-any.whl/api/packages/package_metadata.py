from email.message import EmailMessage
from email.parser import Parser
from pathlib import Path
from typing import List, TYPE_CHECKING, Optional

from pkm.api.dependencies.dependency import Dependency

from pkm.api.versions.version import StandardVersion, Version
from pkm.api.versions.version_specifiers import VersionSpecifier, AllowAllVersions
from pkm.config.configuration import FileConfiguration, computed_based_on
from pkm.utils.dicts import get_or_put, remove_none_values

if TYPE_CHECKING:
    from pkm.api.projects.pyproject_configuration import ProjectConfig

_METADATA_VERSION = '2.1'

_MULTI_FIELDS = {
    'Provides-Extra', 'Platform', 'Supported-Platform', 'Classifier', 'Requires-Dist', 'Provides-Dist',
    'Obsoletes-Dist', 'Requires-External', 'Project-URL', 'Dynamic'
}


class PackageMetadata(FileConfiguration):
    dependencies: List[Dependency]
    required_python_spec: VersionSpecifier

    """
    implementation of the package metadata 2.1 specification as described in pep 566
    see also: https://packaging.python.org/en/latest/specifications/core-metadata/
    """

    @computed_based_on("Metadata-Version")
    def metadata_version(self) -> StandardVersion:
        return StandardVersion.parse(self['Metadata-Version'])

    @property
    def package_name(self) -> str:
        return self['Name']

    @property
    def summary(self) -> Optional[str]:
        return self['Summary']

    @property
    def description(self) -> Optional[str]:
        return self['Description']

    @computed_based_on("Version")
    def package_version(self) -> Version:
        return Version.parse(self['Version'])

    @computed_based_on("Requires-Dist")
    def dependencies(self) -> List[Dependency]:
        requires_dist = self["Requires-Dist"] or []
        return [Dependency.parse(d) for d in requires_dist]

    @dependencies.modifier
    def set_dependencies(self, new_dependencies: List[Dependency]):
        self["Requires-Dist"] = [str(it) for it in new_dependencies]

    @computed_based_on("Requires-Python")
    def required_python_spec(self) -> VersionSpecifier:
        if version_str := self["Requires-Python"]:
            return VersionSpecifier.parse(version_str)
        return AllowAllVersions

    def generate_content(self) -> str:
        msg = EmailMessage()
        for key, value in self._data.items():
            if value is None:
                continue

            if key in _MULTI_FIELDS and not isinstance(value, List):
                raise ValueError(f'{key} expected to be a list, found: {value}')

            if key == 'Description':
                continue  # will add it in payload

            if isinstance(value, List):
                for item in value:
                    msg[key] = item
            else:
                msg[key] = value

        if payload := self._data.get("Description"):
            msg.set_payload(payload)

        return msg.as_string()

    @classmethod
    def from_project_config(cls, prjc: "ProjectConfig") -> "PackageMetadata":

        # filling authors and maintainers according to pep-621:
        # 1. If only name is provided, the value goes in Author/Maintainer as appropriate.
        # 2. If only email is provided, the value goes in Author-email/Maintainer-email as appropriate.
        # 3. If both email and name are provided, the value goes in Author-email/Maintainer-email as appropriate,
        #    with the format {name} <{email}> (with appropriate quoting, e.g. using email.headerregistry.Address).
        # 4. Multiple values should be separated by commas.

        author_names = [a.name for a in (prjc.authors or []) if a.name]
        author_emails = [a.email for a in (prjc.authors or []) if a.email]

        maintainer_names = [a.name for a in (prjc.authors or []) if a.name]
        maintainer_emails = [a.email for a in (prjc.authors or []) if a.email]

        extras = list((prjc.optional_dependencies or {}).keys())
        all_deps = prjc.all_dependencies

        data = {
            'Metadata-Version': _METADATA_VERSION,
            'Name': prjc.name, 'Version': str(prjc.version),
            'Summary': prjc.description, 'Description': prjc.readme_content(),
            'Description-Content-Type': prjc.readme_content_type(), 'Keywords': prjc.keywords or [],
            'Author': ', '.join(author_names), 'Author-email': ', '.join(author_emails),
            'Maintainer': ', '.join(maintainer_names), 'Maintainer-email': ', '.join(maintainer_emails),
            'License': prjc.license_content(), 'Classifier': prjc.classifiers,
            'Requires-Dist': [str(d) for d in all_deps], 'Requires-Python': str(prjc.requires_python),
            'Provides-Extra': extras,
            # 'Dynamic': prjc.dynamic or [], add back when pypi supports metadata version 2.2
        }

        return PackageMetadata(data=remove_none_values(data), path=None)

    @classmethod
    def load(cls, path: Path) -> "PackageMetadata":
        if not path.exists():
            return PackageMetadata(path=path, data={})

        parser = Parser()
        with path.open('r', errors="ignore") as path_fd:
            content = parser.parse(path_fd)

            data = {}
            for key, value in content.items():
                if key in _MULTI_FIELDS:
                    get_or_put(data, key, list).append(value)
                elif old_value := data.get(key):
                    if isinstance(old_value, List):
                        old_value.append(value)
                    else:
                        data[key] = [old_value, value]
                else:
                    data[key] = value

        return PackageMetadata(path=path, data=data)
