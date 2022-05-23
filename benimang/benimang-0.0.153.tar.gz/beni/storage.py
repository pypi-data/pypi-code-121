from typing import Any, Final

import beni
import beni.file as bfile


async def get(key: str, default: Any = None):
    storageFile = _getStorageFile(key)
    if storageFile.is_file():
        return await bfile.readYaml(storageFile)
    else:
        return default


async def set(key: str, value: Any):
    storageFile = _getStorageFile(key)
    await bfile.writeYaml(storageFile, value)


async def clear(*keyList: str):
    for key in keyList:
        storageFile = _getStorageFile(key)
        beni.remove(storageFile)


async def clearAll():
    for storageFile in beni.listFile(_storagePath):
        beni.remove(storageFile)

# ------------------------------------------------------------------------------------------

_storagePath: Final = beni.getPathWorkspace('.storage')


def _getStorageFile(key: str):
    return beni.getPath(_storagePath, f'{key}.yaml')
