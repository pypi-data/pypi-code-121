import sys
import re
from enum import Enum
from distutils.version import LooseVersion

from requests import HTTPError

from .version import __version__

from .httputils import portalApiGet


class VersionSupported(Enum):
    YES = 1
    NO = 2
    CAN_UPGRADE = 3

def getSupportedServerVersions():
    try:
        response = portalApiGet("versions?appName=flow360-python-client")
    except HTTPError:
        raise HTTPError('Error in connecting server')

    versions = [re.sub(r".+-", "", item['version']) for item in response]

    if (len(versions) == 0):
        raise RuntimeError('Error in fetching supported versions')

    return versions

def checkClientVersion():
    supportedVersions = getSupportedServerVersions()
    latestVersion = supportedVersions[0]
    currentVersion = __version__

    isSupported = any([LooseVersion(currentVersion) == LooseVersion(v) for v in supportedVersions])

    if not isSupported:
        return VersionSupported.NO, currentVersion

    elif LooseVersion(currentVersion) < LooseVersion(latestVersion):
        return VersionSupported.CAN_UPGRADE, latestVersion    

    else:
        return VersionSupported.YES, currentVersion    

def ClientVersionGetInfo():
    versionStatus, version = checkClientVersion()

    if versionStatus == VersionSupported.NO:
        print("\nYour version of CLI ({}) is no longer supported.".format(version))
    elif versionStatus == VersionSupported.CAN_UPGRADE:
        print("\nNew version of CLI ({}) is now available.".format(version))
    else:
        return

    msg = """
    To upgrade run:
        pip3 install -U flow360client

    """
    print(msg)

    if versionStatus == VersionSupported.NO:
        sys.exit(0)

ClientVersionGetInfo()