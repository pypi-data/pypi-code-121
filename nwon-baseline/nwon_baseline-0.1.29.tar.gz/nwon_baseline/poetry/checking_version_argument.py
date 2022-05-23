import sys

from nwon_baseline.print_helper.colored_printing import print_error
from nwon_baseline.typings import VersionChange


def checking_version_argument() -> VersionChange:
    arguments = sys.argv

    version_options = [
        VersionChange.MAJOR.value,
        VersionChange.MINOR.value,
        VersionChange.PATCH.value,
    ]

    if (
        arguments is None
        or arguments.__len__() < 2
        or arguments[1] not in version_options
    ):
        print_error(
            f"Expecting one argument that can be one of: {', '.join(version_options)}",
        )
        sys.exit()

    return VersionChange(arguments[1])
