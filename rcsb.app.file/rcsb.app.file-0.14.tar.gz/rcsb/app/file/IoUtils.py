##
# File:    IoUtils.py
# Author:  jdw
# Date:    30-Aug-2021
# Version: 0.001
#
# Updates:
##
"""
Collected I/O utilities.
"""

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import asyncio
import functools
import gzip
import hashlib
import logging
import os
import shutil
import typing
import math
import aiofiles

from rcsb.app.file.ConfigProvider import ConfigProvider
from rcsb.app.file.PathUtils import PathUtils
from rcsb.utils.io.FileLock import FileLock

logger = logging.getLogger(__name__)


def wrapAsync(fnc: typing.Callable) -> typing.Awaitable:
    @functools.wraps(fnc)
    def wrap(*args, **kwargs):
        loop = asyncio.get_event_loop()
        func = functools.partial(fnc, *args, **kwargs)
        return loop.run_in_executor(executor=None, func=func)

    return wrap


class IoUtils:
    """Collected utilities request I/O processing.

    1. Upload a single file (only write new versions)
        lock the idcode/contentType
            create the output path
            store data atomically

    2. Upload a single file in parts (only write new versions):
        if a client multipart partSession exists use it otherwise create the new client session
        save part and metadata to new session

        if all parts are present
            assemble parts and do the single file update (above)

    3. Upload tarfile of individual files with common type/format w/ version=next

    Download a single file
    Download/upload a session bundle
    """

    def __init__(self, cP: typing.Type[ConfigProvider]):
        self.__cP = cP
        self.__pathU = PathUtils(self.__cP)
        self.__makedirs = wrapAsync(os.makedirs)
        self.__replace = wrapAsync(os.replace)
        self.__hashSHA1 = wrapAsync(hashlib.sha1)
        self.__hashMD5 = wrapAsync(hashlib.md5)
        self.__hashSHA256 = wrapAsync(hashlib.sha256)
        self.__checkHashAsync = wrapAsync(self.checkHash)
        self.__getHashDigestAsync = wrapAsync(self.getHashDigest)

    async def store(
        self,
        ifh: typing.IO,
        outPath: str,
        mode: typing.Optional[str] = "wb",
        copyMode: typing.Optional[str] = "native",
        hashType: typing.Optional[str] = None,
        hashDigest: typing.Optional[str] = None,
    ) -> typing.Dict:
        """Store data in the input file handle in the specified output path.

        Args:
            ifh (file-like-object): input file object containing target data
            outPath (str): output file path
            mode (str, optional): output file mode
            copyMode (str, optional): concrete copy mode (native|shell). Defaults to 'native'.
            hashType (str, optional): hash type (MD5|SHA1|SHA256). Defaults to 'MD5'.
            hashDigest (str, optional): hash digest. Defaults to None.

        Returns:
            (dict): {"success": True|False, "statusMessage": <text>}
        """
        ok = False
        ret = {"success": False, "statusMessage": None}
        try:
            dirPath, fn = os.path.split(outPath)
            tempPath = os.path.join(dirPath, "." + fn)
            await self.__makedirs(dirPath, mode=0o755, exist_ok=True)
            if copyMode == "shell":
                with open(tempPath, mode) as ofh:  # pylint: disable=unspecified-encoding
                    shutil.copyfileobj(ifh, ofh)
            else:
                async with aiofiles.open(tempPath, mode) as ofh:
                    if copyMode == "native":
                        await ofh.write(ifh.read())
                        await ofh.flush()
                        os.fsync(ofh.fileno())
                    elif copyMode == "gzip_decompress":
                        await ofh.write(gzip.decompress(ifh.read()))
                        await ofh.flush()
                        os.fsync(ofh.fileno())
            #
            ok = True
            if hashDigest and hashType:
                # ok = self.checkHash(tempPath, hashDigest, hashType)
                ok = await self.__checkHashAsync(tempPath, hashDigest, hashType)
                if not ok:
                    ret = {"success": False, "statusCode": 400, "statusMessage": "%s hash check failed" % hashType}
            if ok:
                await self.__replace(tempPath, outPath)

        except Exception as e:
            logger.exception("Internal write error for path %r: %s", outPath, str(e))
            ret = {"success": False, "statusCode": 400, "statusMessage": "Store fails with %s" % str(e)}
        finally:
            ifh.close()
            if os.path.exists(tempPath):
                try:
                    os.unlink(tempPath)
                except Exception:
                    pass
            ret = {"success": True, "statusCode": 200, "statusMessage": "Store completed"}
            logger.info("Completed store with %r (%d)", outPath, os.path.getsize(outPath))
        return ret

    async def storeUpload(
        self,
        ifh: typing.IO,
        repoType: str,
        idCode: str,
        contentType: str,
        partNumber: int,
        contentFormat: str,
        version: str,
        allowOverWrite: bool = True,
        copyMode: str = "native",
        hashType: str = "MD5",
        hashDigest: typing.Optional[str] = None,
    ) -> typing.Dict:
        logger.debug(
            "repoType %r idCode %r contentType %r partNumber %r contentFormat %r version %r copyMode %r", repoType, idCode, contentType, partNumber, contentFormat, version, copyMode
        )

        if not self.__pathU.checkContentTypeFormat(contentType, contentFormat):
            return {"success": False, "statusCode": 405, "statusMessage": "Bad content type and/or format - upload rejected"}

        lockPath = self.__pathU.getFileLockPath(idCode, contentType, partNumber, contentFormat)
        myLock = FileLock(lockPath)
        with myLock:
            logger.debug("am i locked %r", myLock.isLocked())
            outPath = self.__pathU.getVersionedPath(repoType, idCode, contentType, partNumber, contentFormat, version)
            if not outPath:
                return {"success": False, "statusCode": 405, "statusMessage": "Bad content type metadata - cannot build a valid path"}
            elif os.path.exists(outPath) and not allowOverWrite:
                logger.info("Path exists (overwrite %r): %r", allowOverWrite, outPath)
                return {"success": False, "statusCode": 405, "statusMessage": "Encountered existing file - overwrite prohibited"}
            ret = await self.store(ifh, outPath, mode="wb", copyMode=copyMode, hashType=hashType, hashDigest=hashDigest)
        #
        ret["fileName"] = os.path.basename(outPath) if ret["success"] else None
        return ret

    def checkHash(self, pth: str, hashDigest: str, hashType: str) -> bool:
        tHash = self.getHashDigest(pth, hashType)
        return tHash == hashDigest

    def getHashDigest(self, filePath: str, hashType: str = "SHA1", blockSize: int = 65536) -> typing.Optional[str]:
        """Return the hash (hashType) for the input file.

        Args:
            filePath (str): for input file path
            hashType (str, optional): one of MD5, SHA1, or SHA256. Defaults to "SHA1".
            blockSize (int, optional): the size of incremental read operations. Defaults to 65536.

        Returns:
            (str): hash digest or None on failure
        """
        if hashType not in ["MD5", "SHA1", "SHA256"]:
            return None
        try:
            if hashType == "SHA1":
                # hashObj = await self.__hashSHA1()
                hashObj = hashlib.sha1()
            elif hashType == "SHA256":
                # hashObj = await self.__hashSHA256()
                hashObj = hashlib.sha256()
            elif hashType == "MD5":
                # hashObj = await self.__hashMD5()
                hashObj = hashlib.md5()

            with open(filePath, "rb") as ifh:
                for block in iter(lambda: ifh.read(blockSize), b""):
                    hashObj.update(block)
            return hashObj.hexdigest()
        except Exception as e:
            logger.exception("Failing with file %s %r", filePath, str(e))
        return None

    # ---
    async def storeSlice(
        self,
        ifh: typing.IO,
        sliceIndex: int,
        sliceTotal: int,
        sessionId: str,
        copyMode: str = "native",
        hashType: str = "MD5",
        hashDigest: typing.Optional[str] = None,
    ) -> typing.Dict:
        #
        ret = {"success": False, "statusMessage": None}
        lockPath = self.__pathU.getSliceLockPath(sessionId, sliceIndex, sliceTotal)
        slicePath = self.__pathU.getSliceFilePath(sessionId, sliceIndex, sliceTotal)
        with FileLock(lockPath):
            ret = await self.store(ifh, slicePath, mode="wb", copyMode=copyMode, hashType=hashType, hashDigest=hashDigest)
        ret["sliceCount"] = self.getSliceCount(sessionId, sliceTotal)
        return ret

    # ---
    async def finalizeMultiSliceUpload(
        self,
        sliceTotal: int,
        sessionId: str,
        #
        repoType: str,
        idCode: str,
        contentType: str,
        partNumber: int,
        contentFormat: str,
        version: str,
        allowOverWrite: bool = True,
        copyMode: str = "native",
        #
        hashType: str = "MD5",
        hashDigest: typing.Optional[str] = None,
    ) -> typing.Dict:
        logger.info(
            "repoType %r idCode %r contentType %r partNumber %r contentFormat %r version %r copyMode %r", repoType, idCode, contentType, partNumber, contentFormat, version, copyMode
        )
        #
        ret = {"success": False, "statusMessage": None}
        sliceCount = self.getSliceCount(sessionId, sliceTotal)
        if sliceCount < sliceTotal:
            ret["statusCode"] = 400
            ret["sliceCount"] = sliceCount
            ret["statusMessage"] = f"Missing slice(s) {sliceCount}/{sliceTotal}"
            return ret
        #
        lockPath = self.__pathU.getFileLockPath(idCode, contentType, partNumber, contentFormat)
        logger.info("lockPath %r", lockPath)
        #
        with FileLock(lockPath):
            outPath = self.__pathU.getVersionedPath(repoType, idCode, contentType, partNumber, contentFormat, version)
            if not outPath:
                return {"success": False, "statusCode": 405, "statusMessage": "Bad content type metadata - cannot build a valid path"}
            elif os.path.exists(outPath) and not allowOverWrite:
                logger.info("Path exists (overwrite %r): %r", allowOverWrite, outPath)
                return None
            ret = await self.joinSlices(outPath, sessionId, sliceTotal, mode="wb", hashType=hashType, hashDigest=hashDigest)
        return ret

    def haveAllSlices(self, sessionId, sliceTotal) -> bool:
        for cn in range(1, sliceTotal + 1):
            fp = self.__pathU.getSliceFilePath(sessionId, cn, sliceTotal)
            if not os.path.exists(fp):
                return False
        return True

    def getSliceCount(self, sessionId, sliceTotal) -> int:
        sliceCount = 0
        for cn in range(1, sliceTotal + 1):
            fp = self.__pathU.getSliceFilePath(sessionId, cn, sliceTotal)
            if os.path.exists(fp):
                sliceCount += 1
        return sliceCount

    async def joinSlices(
        self, outPath: str, sessionId: str, sliceTotal: int, mode: str = "wb", hashType: typing.Optional[str] = None, hashDigest: typing.Optional[str] = None
    ) -> typing.Dict:
        """Assemble the set of sliced portions in the input session in the specified output path.

        Args:
            outPath (str): output file path
            mode (str, optional): output file mode
            sessionId (str):  session identifier
            sliceTotal (int): number of slices to be assembled into the output file

        Returns:
            (bool): True for success or False otherwise
        """
        ret = {"success": False, "statusMessage": None}
        try:
            dirPath, fn = os.path.split(outPath)
            tempPath = os.path.join(dirPath, "." + fn)
            await self.__makedirs(dirPath, mode=0o755, exist_ok=True)
            async with aiofiles.open(tempPath, mode) as ofh:
                for cn in range(1, sliceTotal + 1):
                    fp = self.__pathU.getSliceFilePath(sessionId, cn, sliceTotal)
                    logger.info("slice path (%r) %r", cn, fp)
                    async with aiofiles.open(fp, "rb") as ifh:
                        await ofh.write(await ifh.read())
                await ofh.flush()
                os.fsync(ofh.fileno())
            #
            ok = True
            if hashDigest and hashType:
                ok = self.checkHash(tempPath, hashDigest, hashType)
                if not ok:
                    ret = {"success": False, "statusCode": 400, "statusMessage": "Slice join %s hash check failed" % hashType}
            if ok:
                logger.info("hashcheck (%r) tempPath %r", ok, tempPath)
                await self.__replace(tempPath, outPath)
                ret = {"success": True, "statusCode": 200, "statusMessage": "Upload join succeeds"}
        except Exception as e:
            logger.exception("Internal write error for path %r: %s", outPath, str(e))
            ret = {"success": False, "statusCode": 400, "statusMessage": "Slice join fails with %s" % str(e)}
        finally:
            ifh.close()
            if os.path.exists(tempPath):
                try:
                    os.unlink(tempPath.name)
                except Exception:
                    pass
        logger.info("leaving join with ret %r", ret)
        return ret

    async def splitFile(self, inputFilePath: str, numSlices: int, sessionId: str, hashType="md5"):
        """Split the input file into

        Args:
            inputFilePath (str): input file path
            sessionId (str): unique session identifier for the split file
            numSlices (int): divide input file into this number of chunks
            hashType (str, optional): hash type  (MD5, SHA1, or SHA256). Defaults to "MD5".

        Returns:
            str: path to the session directory
        """

        prefixName = sessionId + "_"
        myHash = await self.__getHashDigestAsync(inputFilePath, hashType=hashType)
        logger.info("Path %r (%r)", inputFilePath, myHash)
        sessionDirPath = os.path.join(self.__pathU.getSessionDirPath(), sessionId)
        await self.__makedirs(sessionDirPath, mode=0o755, exist_ok=True)

        numBytes = os.path.getsize(inputFilePath)
        sliceSize = int(math.ceil(numBytes / numSlices))  # Need ceil to properly split odd-number bytes into expected number of slices
        logger.info("numBytes (%d) numSlices (%d) slice size %r", numBytes, numSlices, sliceSize)
        print("numBytes (%d) numSlices (%d) slice size %r", numBytes, numSlices, sliceSize)

        await self.__makedirs(sessionDirPath, mode=0o755, exist_ok=True)

        manifestPath = os.path.join(sessionDirPath, "MANIFEST")
        sliceNumber = 0
        async with aiofiles.open(manifestPath, "w") as mfh:
            mfh.write("%s\t%s\n" % (inputFilePath, myHash))
            async with aiofiles.open(inputFilePath, "rb") as ifh:
                chunk = await ifh.read(sliceSize)
                while chunk:
                    sliceNumber += 1
                    sliceName = prefixName + str(sliceNumber)
                    fp = os.path.join(sessionDirPath, sliceName)
                    async with aiofiles.open(fp, "wb") as ofh:
                        await ofh.write(chunk)
                    await mfh.write("%s\n" % sliceName)
                    #
                    chunk = await ifh.read(sliceSize)
        return sessionDirPath
