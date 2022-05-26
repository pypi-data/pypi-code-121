'''Version Type Analyser

This utility parses a SemVer version string, and outputs the corresponding
version "type".

SemVer strings are composed of a version core (e.g. 1.2.3), an optional
pre-release string (e.g. "-dev2") and an optional build string (e.g
"+18256493"). The version type this utility returns is as follows:

- "invalid" if the SemVer version is malformed
- otherwise, "build" if a build string is present
- otherwise, "pre-release" if a pre-release string is present
- otherwise, "release"

Usage:
  versiontype <semver>
  versiontype -h | --help
  versiontype --version


Options:
  -h --help     Show this screen.
  --version     Show version.
'''


import semver
from docopt import docopt


def version_type_semver(version):
    if not semver.VersionInfo.isvalid(version):
        return "invalid"
    ver = semver.VersionInfo.parse(version)
    if ver.build:
        return "build"
    if ver.prerelease:
        return "pre-release"
    return "release"

def version_type_node_semver(version):
    ver = semver.parse(version, loose=False)
    if ver is None:
        return "invalid"
    if ver.build:
        return "build"
    if ver.prerelease:
        return "pre-release"
    return "release"

def version_type(version):
    version = version.lstrip('v')
    # Workaround for name clashing issue between python-semver and semver
    # modules. See https://github.com/python-semver/python-semver/issues/259
    if hasattr(semver, 'VersionInfo'):
        return version_type_semver(version)
    return version_type_node_semver(version)

def main():
    arguments = docopt(__doc__, version='VersionType')
    print(version_type(arguments['<semver>']))

if __name__ == '__main__':
    main()
