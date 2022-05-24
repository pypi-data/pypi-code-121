"""Pretty-printing for package metadata model classes"""
from typing import Union

from colorama import Style, Back, Fore

from omniversion.models import PackagesMetadataList, AvailableUpdates, PackageMetadata, Vulnerabilities, VersionsMatch
from omniversion.models.package_manager import PackageManager
from omniversion.pretty_print.helpers import traffic_light, multiline_indent


def _pretty_print_package_metadata_list(obj: Union[PackagesMetadataList, AvailableUpdates, VersionsMatch,
                                                   Vulnerabilities]) -> str:
    if isinstance(obj, AvailableUpdates):
        def update_description(update: PackageMetadata):
            if update.current is None:
                latest_version_text = f" version {Fore.WHITE}{update.latest} {Style.RESET_ALL}" \
                    if update.latest else ""
                return f"package {Fore.BLACK}{Back.WHITE} `{update.name}` {Style.RESET_ALL}{latest_version_text}" \
                       f" can be installed"
            return f"update for {Fore.BLACK}{Back.WHITE} `{update.name}` {Style.RESET_ALL} available: " \
                   f"{Fore.WHITE}{update.current}{Style.RESET_ALL} -> {Fore.WHITE}{update.latest}{Style.RESET_ALL}"

        def package_manager_summary(package_manager: PackageManager):
            updates_for_pm = AvailableUpdates(package_manager.packages.data)
            summary = traffic_light(updates_for_pm.__repr__(), "green" if len(updates_for_pm) == 0 else "red")
            return "\n".join([
                f"{Back.CYAN} {package_manager.identifier} {Style.RESET_ALL}",
                multiline_indent(summary),
                *[multiline_indent(multiline_indent(update_description(update))) for update in updates_for_pm]
            ])

        package_managers = PackageManager.list_from_packages(obj.data)
        if len(package_managers) == 0:
            return traffic_light('no package managers found', 'amber')
        return "\n".join([package_manager_summary(pm) for pm in package_managers]) + "\n"

    if isinstance(obj, VersionsMatch):
        table_items = [
            f'\t{(item.current or "").ljust(20)}'
            + f'\t{(item.host or "").ljust(12)}'
            + f'\t{(item.package_manager or "").ljust(12)}'
            + f'\t{item.name or ""}'
            for item in obj.data
        ]
        color = "green"
        if len(obj.versions) <= 1 or not obj.is_consistent or not obj.has_all_expected_items:
            color = "red"
        return traffic_light(obj.__str__() + "\n".join(table_items), color)

    if isinstance(obj, Vulnerabilities):
        advisories = [[data_item, advisory] for data_item in obj for advisory in data_item.advisories]
        audit_items = [
            f'\t{(data_item.name or "").ljust(20)}'
            + f'\t{(data_item.host or "").ljust(12)}'
            + f'\t{(data_item.package_manager or "").ljust(12)}'
            + f'\t{advisory.severity or ""}'
            for [data_item, advisory] in advisories
        ]
        return traffic_light(
            f"{obj}\n"
            + "\n".join(audit_items),
            "green" if len(advisories) == 0 else "red")

    # must be a `PackagesMetadataList` object
    num_dependencies = len(obj)
    pretty_deps = "dependenc" + ("y" if num_dependencies == 1 else "ies")
    return f"{num_dependencies} {Style.DIM}{pretty_deps}{Style.RESET_ALL}"
