##
# File:    PathUtils.py
# Author:  jdw
# Date:    25-Aug-2021
# Version: 0.001
#
# Updates:
##
"""
Collected utilities for file system path and file name access.
"""

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import glob
import logging
import os
import typing

from rcsb.app.file.ConfigProvider import ConfigProvider

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PathUtils:
    """Collected utilities for file system path and file name access."""

    def __init__(self, cP: typing.Type[ConfigProvider]):
        self.__cP = cP
        self.__repositoryDirPath = self.__cP.get("REPOSITORY_DIR_PATH")
        self.__sessionDirPath = self.__cP.get("SESSION_DIR_PATH")
        self.__sharedLockDirPath = self.__cP.get("SHARED_LOCK_PATH")
        self.__contentTypeInfoD = self.__cP.get("CONTENT_TYPE")
        self.__fileFormatExtensionD = self.__cP.get("FILE_FORMAT_EXTENSION")

    def getSessionDirPath(self) -> str:
        return self.__sessionDirPath

    def getSharedLockDirPath(self) -> str:
        return self.__sharedLockDirPath

    def getRepositoryDirPath(self, repositoryType: str) -> typing.Optional[str]:
        if repositoryType.lower() in ["onedep-archive", "archive"]:
            return os.path.join(self.__repositoryDirPath, "archive")
        elif repositoryType.lower() in ["onedep-deposit", "deposit"]:
            return os.path.join(self.__repositoryDirPath, "deposit")
        return None

    def getFileLockPath(self, idCode: str, contentType: str, partNumber: int, contentFormat: str) -> str:
        lockPath = self.getSharedLockDirPath()
        fnBase = self.__getBaseFileName(idCode, contentType, partNumber, contentFormat)
        return os.path.join(lockPath, fnBase + ".lock")

    def getSliceFilePath(self, sessionId: str, sliceIndex: int, sliceTotal: int) -> str:
        sessionPath = self.getSessionDirPath()
        fnBase = f"{sessionId}_{sliceIndex}.{sliceTotal}"
        return os.path.join(sessionPath, sessionId, fnBase)

    def getSliceLockPath(self, sessionId: str, sliceIndex: int, sliceTotal: int) -> str:
        lockPath = self.getSharedLockDirPath()
        fnBase = f"{sessionId}_{sliceIndex}.{sliceTotal}"
        return os.path.join(lockPath, fnBase + ".lock")

    def getVersionedPath(self, repositoryType: str, idCode: str, contentType: str, partNumber: int, contentFormat: str, version: str) -> typing.Optional[str]:
        fTupL = []
        filePath = None
        try:
            repoPath = self.getRepositoryDirPath(repositoryType)
            fnBase = self.__getBaseFileName(idCode, contentType, partNumber, contentFormat) + ".V"
            filePattern = os.path.join(repoPath, idCode, fnBase)
            if version.isdigit():
                filePath = filePattern + str(version)
            else:
                # JDW wrap this for async?
                for pth in glob.iglob(filePattern + "*"):
                    vNo = int(pth.split(".")[-1][1:])
                    fTupL.append((pth, vNo))
                # - sort in decending version order -
                if len(fTupL) > 1:
                    fTupL.sort(key=lambda tup: tup[1], reverse=True)
                #
                if version.lower() == "next":
                    if fTupL:
                        filePath = filePattern + str(fTupL[0][1] + 1)
                    else:
                        filePath = filePattern + str(1)
                    #
                elif version.lower() in ["last", "latest"]:
                    if fTupL:
                        filePath = fTupL[0][0]
                    #
                elif version.lower() in ["prev", "previous"]:
                    if len(fTupL) > 1:
                        filePath = fTupL[1][0]
                    #
                elif version.lower() in ["first"]:
                    if fTupL:
                        filePath = fTupL[-1][0]
                    #
                elif version.lower() in ["second"]:
                    if len(fTupL) > 1:
                        filePath = fTupL[-2][0]
                    #
                #
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return filePath

    def checkContentTypeFormat(self, contentType: str = None, contentFormat: str = None) -> bool:
        ok = False
        try:
            if (not contentType) and (not contentFormat):
                logger.info("No 'contentType' and 'contentFormat' defined.")
            #
            elif contentType:
                if contentType in self.__contentTypeInfoD:
                    if contentFormat:
                        if contentFormat in self.__contentTypeInfoD[contentType][0]:
                            logger.info("System supports %s contentType with %s contentFormat.", contentType, contentFormat)
                            ok = True
                        else:
                            logger.info("System does not support %s contentType with %s contentFormat.", contentType, contentFormat)
                    else:
                        logger.info("System supports %s contentType.", contentType)
                        ok = True
                else:
                    logger.info("System does not support %s contentType.", contentType)
                #
            elif contentFormat:
                if contentFormat in self.__fileFormatExtensionD:
                    logger.info("System supports %s contentFormat.", contentFormat)
                    ok = True
                else:
                    logger.info("System does not support %s contentFormat.", contentFormat)
                #
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            ok = False
        return ok
        #

    def getMimeType(self, contentFormat: str) -> str:
        cFormat = contentFormat
        if self.__fileFormatExtensionD and (contentFormat in self.__fileFormatExtensionD) and self.__fileFormatExtensionD[contentFormat]:
            cFormat = self.__fileFormatExtensionD[contentFormat]
        #
        if cFormat in ["cif"]:
            mt = "chemical/x-mmcif"
        elif cFormat in ["pdf"]:
            mt = "application/pdf"
        elif cFormat in ["xml"]:
            mt = "application/xml"
        elif cFormat in ["json"]:
            mt = "application/json"
        elif cFormat in ["txt"]:
            mt = "text/plain"
        elif cFormat in ["pic"]:
            mt = "application/python-pickle"
        else:
            mt = "text/plain"
        #
        return mt

    def __getBaseFileName(self, idCode: str, contentType: str, partNumber: int, contentFormat: str) -> str:
        return f"{idCode}_{self.__contentTypeInfoD[contentType][1]}_P{partNumber}.{self.__fileFormatExtensionD[contentFormat]}"
