"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import json
from uuid import uuid4, uuid5, NAMESPACE_URL
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from . import bdio_paths
from ..custom_types import JsonDict, ExtendedFullPath
from ..version_king import parse_go_pseudoversion


def count_components(bdio: JsonDict) -> int:
    return len(get_components(bdio))


def get_components(bdio: JsonDict) -> List[JsonDict]:
    components = get_bdio_entries_by_type(bdio, "Component")
    if components:
        return components
    return get_bdio_entries_by_type(bdio, "https://blackducksoftware.github.io/bdio#Component")


def get_files(bdio: JsonDict) -> List[JsonDict]:
    files = get_bdio_entries_by_type(bdio, "File")
    if files:
        return files
    return get_bdio_entries_by_type(bdio, "https://blackducksoftware.github.io/bdio#File")


def get_bdio_entries_by_type(bdio: JsonDict, type_id: str) -> List[JsonDict]:
    result: List[JsonDict] = []  # for the dear stupid mypy who cannot infer this but just nags
    if "@graph" not in bdio:
        return result
    for entry in bdio["@graph"]:
        type_value = entry.get("@type")
        if isinstance(type_value, list) and type_value[0] == type_id:
            result.append(entry)
        elif type_value == type_id:
            result.append(entry)
    return result


def get_all_extended_fileentries(scanner_results: List[JsonDict]) -> List[ExtendedFullPath]:
    result = []
    for component_info in scanner_results:
        for extended_obj in component_info["extended-objects"]:
            extended_fullpath = extended_obj.get("extended-fullpath")
            if not extended_fullpath:
                continue  # some old scans do not have those
            result.append(extended_fullpath)
    return result


def get_all_fileentries_bdio(bdio_content: JsonDict) -> List[ExtendedFullPath]:
    extended_fullpaths: List[ExtendedFullPath] = []
    for file_entry_bdio in get_files(bdio_content):
        if "path" in file_entry_bdio:
            file_path_bdio = file_entry_bdio["path"]
        elif "https://blackducksoftware.github.io/bdio#hasPath" in file_entry_bdio:
            file_path_bdio = file_entry_bdio["https://blackducksoftware.github.io/bdio#hasPath"][0][
                "@value"
            ]
        else:
            continue
        extended_fullpath = bdio_paths.bdio_path_uri_to_fullpath(file_path_bdio)
        extended_fullpaths.append(extended_fullpath)
    return extended_fullpaths


def split_version_from_external_id(forge: str, identifier: str) -> Tuple[str, str]:
    name_version_cutoff = 1
    if forge == "maven":
        # Maven entries have group and artifact parts separated with separator
        name_version_cutoff = 2
    separator = BDIOEntries.forge_to_separator_char.get(forge, "/")
    parts = identifier.split(separator)
    return separator.join(parts[:name_version_cutoff]), separator.join(parts[name_version_cutoff:])


def dump_bdio_to_file(bdio: JsonDict, filepath: str) -> None:
    with open(filepath, "w") as fd:
        json.dump(bdio, fd, indent=4, sort_keys=True, ensure_ascii=False)


def mangle_go_version(version: Optional[str]) -> Optional[str]:
    """
    BD KB Go component versions are in pre-go.mod format.
    Mangle go.mod -style versions to match KB.
    """
    # Non go.mod dependency
    if not version:
        return version

    if version.endswith("+incompatible"):
        version = version.replace("+incompatible", "")

    try:
        _, gittag = parse_go_pseudoversion(version)
        version = gittag
    except ValueError:
        pass
    return version


def _format_datetime(date: datetime) -> str:
    # BD datetime parser needs an offset at the end
    return date.isoformat() + "Z"


#    return date.strftime("%Y-%m-%dT%H:%M:%SZ")
# is fixed in py3 by using the timezone class from datetime and giving that as an argument
# when retrieving the time. Then isoformat() will add it to the print


class BDIOEntries:
    """
    Low level factory methods to create JSON dicts according to the BDIO syntax
    for various entities and datatypes used in BDBA.
    For combining the produced entries see and use the BDIOBuilder.

    See also https://github.com/blackducksoftware/bdio/tree/master/bdio2/src/main/java/com/blackducksoftware/bdio2/model
    for standard implementation.
    """

    forge_to_separator_char = {
        "alpine": "/",
        "anaconda": "/",
        "android_sdk": "/",
        "apache_software": "/",
        "arch_linux": "/",
        "automotive_linux": "/",
        "bower": "/",
        "centos": "/",
        "clearlinux": "/",
        "codeplex": "/",
        "codeplex_group": "/",
        "cpan": "/",
        "cran": "/",
        "crates": "/",
        "dart": "/",
        "debian": "/",
        "eclipse": "/",
        "fedora": "/",
        "freedesktop_org": "/",
        "github_gist": "/",
        "googlecode": "/",
        "hackage": "/",
        "hex": "/",
        "java_net": "/",
        "kde_org": "/",
        "launchpad": "/",
        "mongodb": "/",
        "npmjs": "/",
        "nuget": "/",
        "openembedded": "/",
        "opensuse": "/",
        "oracle_linux": "/",
        "pear": "/",
        "pypi": "/",
        "redhat": "/",
        "ros": "/",
        "rubyforge": "/",
        "rubygems": "/",
        "runtime": "/",
        "sourceforge": "/",
        "sourceforge_jp": "/",
        "tianocore": "/",
        "ubuntu": "/",
        "yocto": "/",
        "alt_linux": ":",
        "android": ":",
        "bitbucket": ":",
        "cocoapods": ":",
        "cpe": ":",
        "efisbot": ":",
        "gitcafe": ":",
        "github": ":",
        "gitlab": ":",
        "gitorious": ":",
        "gnu": ":",
        "golang": ":",
        "maven": ":",
        "openjdk": ":",
        "packagist": ":",
        "protecode_sc": ":",
        "long_tail": "#",
        "conan": "$",
    }

    @staticmethod
    def component(forge: str, identifier: str, fallback_forge: bool = False) -> JsonDict:
        component = {
            "@type": "Component",
            "@id": f"urn:uuid:{uuid4()}",
            "identifier": identifier,
        }
        if fallback_forge:
            # the @ denotes a class of forges, the Hub looks into alternative forges aka
            # fallback forges if it cannot find stuff in this one
            component["namespace"] = f"@{forge}"
        else:
            component["namespace"] = f"{forge}"

        return component

    @staticmethod
    def fileentry(
        extended_fullpath: ExtendedFullPath,
        timestamp: int,
        sha1: str,
        filesize: Optional[int] = None,
        annotation: Optional[JsonDict] = None,
        original_scanned_filename: Optional[str] = None,
    ) -> JsonDict:
        """
        Describe a file with its path and various other attributes.
        """
        if original_scanned_filename:
            # first file has a name in the scan project that might have been changed during the
            # upload to some temporary random file name, so patch it back here
            extended_fullpath[0] = extended_fullpath[0].copy()
            extended_fullpath[0]["path"] = original_scanned_filename

        fileentry_bdio: JsonDict = {  # required typing due to later int value added
            "@type": "File",
            "@id": f"urn:uuid:{uuid4()}",
            "path": bdio_paths.fullpath_to_bdio_path_uri(extended_fullpath),
            # choices for us below are: "regular", "regular/binary",
            # "directory/archive", "regular/text"
            # TODO: omit this for now as bdio linter chokes on wrong types
            # and currently we do not have any logic below to omit the right type, e.g.directory
            # "fileSystemType": "regular/binary",
            "fingerprint": f"sha1:{sha1}",
            "lastModifiedDateTime": _format_datetime(datetime.utcfromtimestamp(timestamp)),
        }
        # some older results might not have the filesize - introduced around 2019
        if filesize:
            fileentry_bdio["byteCount"] = filesize
        if annotation:
            fileentry_bdio["description"] = annotation["@id"]
        return fileentry_bdio

    @staticmethod
    def fileentry_project_base(scanned_path: str, filesize: Optional[int] = None) -> JsonDict:
        extended_fullpath = [{"type": "file", "path": scanned_path}]
        bdio_path = bdio_paths.fullpath_to_bdio_path_uri(extended_fullpath)
        # if no component findings were in the toplevel file then we will not have a cached
        # fileentry_from_extended_fullpath for it and need to create one here with not all file properties known
        fileentry_bdio: JsonDict = {
            "@type": "File",
            "@id": f"urn:uuid:{uuid4()}",
            "path": bdio_path,
        }
        if filesize:
            fileentry_bdio["byteCount"] = filesize
        # TODO: would need to find out if it was a file or directory that we scanned
        # and choose the type accordingly. Difficult though with those temporary downloaded files
        # "fileSystemType": "directory/archive",
        return fileentry_bdio

    @staticmethod
    def evidence_file(
        componententry: JsonDict,
        fileentry: JsonDict,
        match_type: str = "binary",
        annotation: Optional[JsonDict] = None,
    ) -> JsonDict:
        """
        Tells where a component was found, in which file.
        """
        dependency = {
            "@type": "Dependency",
            "dependsOn": componententry["@id"],
            "evidence": fileentry["@id"],
        }
        if match_type:
            dependency["matchType"] = match_type
        if annotation:
            dependency["description"] = annotation["@id"]
        return dependency

    @staticmethod
    def dependency_transitive_entry(
        dependency_component: JsonDict,
        match_type: str = "transitive dependency",
        annotation: Optional[JsonDict] = None,
    ) -> JsonDict:
        """
        Creates component links that are dependencies for another component.
        """
        dependency = {
            "@type": "Dependency",
            "dependsOn": dependency_component["@id"],
        }
        if match_type:
            dependency["matchType"] = match_type
        if annotation:
            dependency["description"] = annotation["@id"]
        return dependency

    @staticmethod
    def toplevel_graph(
        publisher: str,
        publisher_version: str,
        code_location_name: str,
        code_location_uri: Optional[str] = None,
        code_location_uri_auto: bool = False,
    ) -> JsonDict:
        """
        Top level bdio file content.
        """
        contents: List[JsonDict] = []
        result = {
            "@graph": contents,
            "@context": [
                "https://blackducksoftware.github.io/bdio/2.0.0",
                {"matchType": "https://blackducksoftware.com/hub#hasHubFileMatchType"},
            ],
            "creationDateTime": _format_datetime(datetime.utcnow()),
            "name": code_location_name,
            "publisher": f"{publisher}/{publisher_version}",
        }
        if code_location_uri:
            result["@id"] = code_location_uri
        if code_location_uri_auto:
            result["@id"] = f"urn:uuid:{uuid5(NAMESPACE_URL, code_location_name)}"
        return result

    @staticmethod
    def project(
        name: str,
        version: Optional[str],
        fileentry_project_base: JsonDict,
        description: Optional[JsonDict] = None,
    ) -> JsonDict:
        contents: List[JsonDict] = []
        project = {
            "@type": "Project",
            "@id": f"urn:uuid:{uuid4()}",
            "name": name,
            "base": fileentry_project_base["@id"],
            "dependency": contents,
        }
        if version is not None:
            project["version"] = version
        if description:
            project["description"] = description["@id"]
        return project

    @staticmethod
    def annotation(content: str) -> JsonDict:
        """
        Any note, comment etc.
        """
        annotation = {
            "@type": "Annotation",
            "@id": f"urn:uuid:{uuid4()}",
            "comment": content,
        }
        return annotation

    @staticmethod
    def external_id(
        forge: str,
        component_name: str,
        *id_parts: Optional[str],
        forge_separator_override: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Returns a BD external-id as a tuple of (forge, identifier)
        """
        result_id_parts = [component_name]
        for id_part in id_parts:
            if id_part:
                result_id_parts.append(id_part)
        # default to slash as separator as most linux distros use that and we are dynamic in
        # discovering those from files
        if forge_separator_override:
            separator = forge_separator_override
        else:
            separator = BDIOEntries.forge_to_separator_char.get(forge, "/")
        return forge, separator.join(result_id_parts)


class BDIOBuilder:
    """
    A builder object for BDIO file contents.
    An example skeleton for creating a BDIO file. Note that bdio_file and project need to be
    created at the beginning as the other entities will be added to those:

    builder = BDIOBuilder()
    builder.bdio_file()
    builder.project()
    file = builder.fileentry_...()
    component = builder.component()
    annotation = builder.annotation()
    builder.dependency(component, file, annotation)
    ...
    return builder.get_result()
    """

    def __init__(self):
        self.toplevel_element: JsonDict = {}
        self.project_element: JsonDict = {}
        # below dicts are caches
        self.unique_component_entries: Dict[Tuple[str, str], JsonDict] = {}
        self.fileentry_by_bdio_path: Dict[str, JsonDict] = {}
        self.unique_annotations: Dict[str, JsonDict] = {}

    def _add_to_toplevel(self, entry: JsonDict) -> None:
        if not self.toplevel_element:
            raise ValueError("Toplevel element not set!")
        if "@graph" not in self.toplevel_element:
            raise ValueError("Toplevel missing '@graph' entry")

        self.toplevel_element["@graph"].append(entry)

    def _add_to_project(self, entry: JsonDict) -> None:
        if not self.project_element:
            raise ValueError("Project element not set!")
        if "dependency" not in self.project_element:
            raise ValueError("Project element missing 'dependency' entry!")

        self.project_element["dependency"].append(entry)

    def bdio_file(
        self,
        publisher: str,
        publisher_version: str,
        code_location_name: str,
        code_location_uri: Optional[str] = None,
        code_location_uri_auto: bool = False,
    ) -> JsonDict:
        """
        Top level bdio file content, also known as Graph in other places.
        """
        self.toplevel_element = BDIOEntries.toplevel_graph(
            publisher,
            publisher_version,
            code_location_name,
            code_location_uri,
            code_location_uri_auto,
        )
        return self.toplevel_element

    def project(
        self,
        name: str,
        version: str,
        fileentry_project_base: JsonDict,
        description: Optional[JsonDict] = None,
    ) -> JsonDict:
        if self.project_element:
            raise ValueError("Project element existing already. Only 1 allowed.")
        self.project_element = BDIOEntries.project(
            name, version, fileentry_project_base, description
        )
        self._add_to_toplevel(self.project_element)
        return self.project_element

    def fileentry_from_extended_object(
        self,
        extended_object: JsonDict,
        annotation: Optional[JsonDict] = None,
        original_scanned_filename: Optional[str] = None,
    ) -> JsonDict:
        extended_fullpath = extended_object.get("extended-fullpath")
        if not extended_fullpath:
            # older scan results do not have extended-fullpaths so need to mock them
            extended_fullpath = bdio_paths.simple_fullpath_to_extended_fullpath(
                extended_object["fullpath"]
            )
        filesize = extended_object.get("size")  # again to deal with older scans
        sha1 = extended_object["sha1"]
        timestamp = extended_object["timestamp"]
        return self.fileentry_from_extended_fullpath(
            extended_fullpath, timestamp, sha1, filesize, annotation, original_scanned_filename
        )

    def fileentry_from_extended_fullpath(
        self,
        extended_fullpath: ExtendedFullPath,
        timestamp: int,
        sha1: str,
        filesize: Optional[int] = None,
        annotation: Optional[JsonDict] = None,
        original_scanned_filename: Optional[str] = None,
    ) -> JsonDict:
        """
        Describe a file with its path and various other attributes.
        """
        # first file has a name in the scan project that might have been changed during the
        # upload to some temporary random file name, so patch it back here
        fileentry_bdio = BDIOEntries.fileentry(
            extended_fullpath, timestamp, sha1, filesize, annotation, original_scanned_filename
        )
        bdio_path = fileentry_bdio["path"]
        cached_fileentry_bdio = self.fileentry_by_bdio_path.get(bdio_path)
        if not cached_fileentry_bdio:
            self.fileentry_by_bdio_path[bdio_path] = fileentry_bdio
            self._add_to_toplevel(fileentry_bdio)
            cached_fileentry_bdio = fileentry_bdio
        return cached_fileentry_bdio

    def fileentry_from_fullpath(
        self,
        fullpath: List[str],
        timestamp: int,
        sha1: str,
        filesize: Optional[int] = None,
        annotation: Optional[JsonDict] = None,
        original_scanned_filename: Optional[str] = None,
    ) -> JsonDict:
        """
        Describe a file with its path and various other attributes.
        """
        extended_fullpath = bdio_paths.simple_fullpath_to_extended_fullpath(fullpath)
        return self.fileentry_from_extended_fullpath(
            extended_fullpath, timestamp, sha1, filesize, annotation, original_scanned_filename
        )

    def fileentry_project_base(self, scanned_path: str, filesize: Optional[int] = None) -> JsonDict:
        fileentry_bdio = BDIOEntries.fileentry_project_base(scanned_path, filesize)
        bdio_path = fileentry_bdio["path"]
        cached_fileentry_bdio = self.fileentry_by_bdio_path.get(bdio_path)
        if not cached_fileentry_bdio:
            self.fileentry_by_bdio_path[bdio_path] = fileentry_bdio
            self._add_to_toplevel(fileentry_bdio)
            cached_fileentry_bdio = fileentry_bdio
        return cached_fileentry_bdio

    def evidence_file(
        self,
        component_entry: JsonDict,
        fileentry: JsonDict,
        match_type: str = "binary",
        annotation: Optional[JsonDict] = None,
    ) -> JsonDict:
        """
        Tells where a component was found, in which file.

        :param component_entry: a component entry created with this builder
        :param fileentry: a file entry created with this builder that is the evidence
                            for the component
        :param match_type: one of "binary, manual, file, partial_file, snippet, dependency"
        :param annotation: any text annotation that should be linked to this
        """
        dependency = BDIOEntries.evidence_file(component_entry, fileentry, match_type, annotation)
        self._add_to_project(dependency)
        return dependency

    def dependency_direct(
        self,
        component_entry: JsonDict,
    ) -> JsonDict:
        """
        Just a component entry, without link to any evidence. Usually from a package manager.
        """
        # a direct dependency is just a component without any other references to it, e.g.
        # files or other components, so only thing to do is to make sure this component
        # is added to the graph
        forge = component_entry["namespace"]
        identifier = component_entry["identifier"]
        self.component_from_id(
            forge, identifier
        )  # this is a no-op if the component was already added
        return component_entry

    def dependency_direct_with_evidence_file(
        self,
        component_entry: JsonDict,
        fileentry: JsonDict,
        match_type: str = "binary",
        annotation: Optional[JsonDict] = None,
    ) -> JsonDict:
        self.dependency_direct(component_entry)
        # the duplicated component is necessary because the Hub internal magic on deciding matching
        # types and showing evidence is quite a bunch of ... and would not show the file if
        # it is associated with a direct dependency component. Hence the need to add another
        # component of the same ID which will be collated in the Hub view. This is a HACK!
        component_copy = self.component_copy(component_entry)
        return self.evidence_file(component_copy, fileentry, match_type, annotation)

    @staticmethod
    def dependency_transitive(
        component_entry: JsonDict,
        component_transitive: JsonDict,
        match_type: str = "transitive dependency",
        annotation: Optional[JsonDict] = None,
    ) -> JsonDict:
        """
        A component that is pulled in by another component as a transitive dependency.

        :param component_entry: a component entry created with this builder
        :param component_transitive: a component entry created with this builder on which the
                                        above component depends on
        :param match_type: one of "binary, manual, file, partial_file, snippet, dependency"
        :param annotation: any text annotation that should be linked to this

        """
        dependency_entry = BDIOEntries.dependency_transitive_entry(
            component_transitive, match_type, annotation
        )
        component_entry["dependency"] = component_entry.get("dependency", [])
        component_entry["dependency"].append(dependency_entry)
        return component_entry

    def dependency_transitive_with_evidence_file(
        self,
        component_entry: JsonDict,
        component_transitive: JsonDict,
        fileentry_transitive: JsonDict,
        match_type_transitive: str = "transitive dependency",
        match_type_file: str = "binary",
        annotation: Optional[JsonDict] = None,
    ) -> JsonDict:
        self.dependency_transitive(
            component_entry, component_transitive, match_type_transitive, annotation
        )
        # the duplicated component is necessary because the Hub internal magic on deciding matching
        # types and showing evidence is quite a bunch of ... and would not show the file if
        # it is associated with a direct dependency component. Hence the need to add another
        # component of the same ID which will be collated in the Hub view. This is a HACK!
        component_copy = self.component_copy(component_transitive)
        return self.evidence_file(component_copy, fileentry_transitive, match_type_file, annotation)

    def component_from_id(
        self, forge: str, identifier: str, fallback_forge: bool = False, allow_duplicates=False
    ) -> JsonDict:
        component = self.unique_component_entries.get((forge, identifier))
        if not component or allow_duplicates:
            # if we add a duplicate here then that will be the one returned next time
            component = BDIOEntries.component(forge, identifier, fallback_forge=fallback_forge)
            self.unique_component_entries[(forge, identifier)] = component
            self._add_to_toplevel(component)
        return component

    def component(
        self,
        forge: str,
        component_name: str,
        *id_parts: Optional[str],
        forge_separator_override: Optional[str] = None,
        fallback_forge: bool = False,
        allow_duplicates=False,
    ) -> JsonDict:
        forge, identifier = BDIOEntries.external_id(
            forge, component_name, *id_parts, forge_separator_override=forge_separator_override
        )
        return self.component_from_id(
            forge, identifier, fallback_forge=fallback_forge, allow_duplicates=allow_duplicates
        )

    def component_copy(self, component: JsonDict) -> JsonDict:
        forge = component["namespace"]
        identifier = component["identifier"]
        return self.component_from_id(forge, identifier, allow_duplicates=True)

    def tool_comment(self) -> JsonDict:
        """
        Appcheck was here!
        """
        return self.annotation("Here be Binary Ducks and Dragons!")

    def matching_info(self, extended_object: JsonDict) -> JsonDict:
        """
        An annotation containing some more information bits from our matching
        to help with debugging later.
        """
        # some of the fields below did not always exist so be careful with older results
        matching_methods = extended_object.get("matching-methods")
        if not matching_methods:
            matching_method = extended_object.get("matching-method")
            matching_methods = [matching_method] if matching_method else []
        matching_methods_string = (
            f" matching-methods: {matching_methods};" if matching_methods else ""
        )

        codetype = extended_object.get("type")
        codetype_string = f" codetype: {codetype};" if codetype else ""
        confidence = extended_object.get("confidence")
        confidence_string = f"matching-confidence: {confidence};" if confidence else ""

        return self.annotation(f"{confidence_string}{matching_methods_string}{codetype_string}")

    def annotation(self, content: str) -> JsonDict:
        """
        Any note, comment etc.
        """
        annotation = self.unique_annotations.get(content)
        if not annotation:
            annotation = BDIOEntries.annotation(content)
            self.unique_annotations[content] = annotation
            self._add_to_toplevel(annotation)
        return annotation

    def get_result(self) -> JsonDict:
        return self.toplevel_element
