##
# File:    ConfigProvider.py
# Author:  jdw
# Date:    16-Aug-2021
# Version: 0.001
#
# Updates:
##
"""
Accessors for configuration details.
"""

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import datetime
import logging
import os
import typing

from mmcif.api.DataCategoryBase import DataCategoryBase
from rcsb.utils.config.ConfigUtil import ConfigUtil
from rcsb.utils.io.MarshalUtil import MarshalUtil
from rcsb.utils.io.SingletonClass import SingletonClass

logger = logging.getLogger(__name__)


class ConfigProvider(SingletonClass):
    """Accessors for configuration details."""

    def __init__(self, cachePath: typing.Optional[str] = None, configFilePath: typing.Optional[str] = None):
        # ---
        self.__cachePath = cachePath if cachePath else os.environ.get("CACHE_PATH", os.path.abspath("./CACHE"))
        self.__configFilePath = configFilePath if configFilePath else os.environ.get("CONFIG_FILE")
        # logger.info("CONFIG Using CACHE_PATH setting %r", self.__cachePath)
        # logger.info("CONFIG Using CONFIG_FILE path %r", self.__configFilePath)
        self.__mU = MarshalUtil(workPath=self.__cachePath)
        self.__configD = None
        self.__dataObj = None
        # ---

    def get(self, ky: str) -> typing.Optional[str]:
        try:
            if not self.__configD:
                if self.__configFilePath:
                    self.__readConFigFromConFigYmlFile()
                # else:
                #    self.__readConfig()
                #
            return self.__configD["data"][ky]
        except Exception:
            pass
        return None

    def getConfig(self) -> typing.Dict:
        try:
            if not self.__configD:
                if self.__configFilePath:
                    self.__readConFigFromConFigYmlFile()
                # else:
                #    self.__readConfig()
                #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return self.__configD["data"]

    def getData(self) -> typing.Type[DataCategoryBase]:
        try:
            if not self.__dataObj:
                self.__readData()
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return self.__dataObj

    def getVersion(self) -> typing.Optional[str]:
        try:
            return self.__configD["version"]
        except Exception:
            pass
        return None

    def __readData(self, fileName: str = "example-data.cif") -> bool:
        """Read example data file ... this is used for testing the startup of the application,
        to make sure it can find and read a data file.

        Data file should be in pre-configured location.

        Returns:
            bool: True for success or False otherwise
        """
        ok = False
        try:
            dataFilePath = os.path.join(self.__cachePath, fileName)
            dataObj = None
            if self.__mU.exists(dataFilePath):
                dataObjL = self.__mU.doImport(dataFilePath, fmt="mmcif")
                if dataObjL and dataObjL[0]:
                    nL = dataObjL[0].getObjNameList()
                    logger.debug("nL %r", nL)
                    ok = len(nL) >= 6
                    dataObj = dataObjL[0]
            else:
                # Handle missing config for now
                logger.warning("Reading data file fails from path %r", dataFilePath)
                ok = True
            #
            self.__dataObj = dataObj
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            ok = False
        return ok

    def __readConFigFromConFigYmlFile(self) -> bool:
        """Read Yml configuration file and set internal configuration dictionary"""
        ok = False
        try:
            cfgOb = ConfigUtil(configPath=self.__configFilePath, defaultSectionName="configuration", mockTopPath=None)
            self.__configD = {"version": 0.30, "created": datetime.datetime.now().isoformat(), "data": cfgOb.exportConfig(sectionName="configuration")}
            ok = True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            ok = False
        return ok

    # def __readConfig(self) -> bool:
    #     """Read example configuration file and set internal configuration dictionary

    #     Returns:
    #         bool: True for success or False otherwise
    #     """
    #     #
    #     ok = False
    #     try:
    #         configFilePath = self.__getConfigFilePath()
    #         configD = {}
    #         if self.__mU.exists(configFilePath):
    #             configD = self.__mU.doImport(configFilePath, fmt="json")
    #         logger.debug("configD: %r", configD)
    #         if configD and (len(configD) >= 2) and float(configD["version"]) > 0.1:
    #             logger.info("Read version %r sections %r from %s", configD["version"], list(configD.keys()), configFilePath)
    #             ok = True

    #         else:
    #             # Handle missing config for now
    #             logger.warning("Reading config file fails from path %r", configFilePath)
    #             logger.warning("Using config %r", configD)
    #             ok = True
    #         #
    #         self.__configD = configD
    #     except Exception as e:
    #         logger.exception("Failing with %s", str(e))
    #         ok = False
    #     return ok

    # def __getConfigFilePath(self) -> str:
    #     fileName = "example-config.json"
    #     configFilePath = os.path.join(self.__cachePath, "config", fileName)
    #     return configFilePath

    # def setConfig(self, configData: typing.Optional[typing.Dict] = None) -> bool:
    #     """Provide bootstrap configuration options.

    #     Args:
    #         cachePath (str): path to cache data files.

    #     Returns:
    #         bool: True for success or False otherwise

    #     """
    #     self.__configD = self.__makeBootstrapDepictConfig(configData=configData)
    #     return len(self.__configD) >= 2

    # def __makeBootstrapDepictConfig(self, storeConfig: typing.Optional[bool] = True, configData: typing.Optional[typing.Dict] = None) -> typing.Dict:
    #     """Create example configuration bootstrap file"""
    #     configD = {}
    #     try:
    #         cD = configData if configData else {}
    #         configFilePath = self.__configFilePath
    #         configDirPath = os.path.dirname(configFilePath)
    #         logger.debug("Updating example configuration using %s", configFilePath)
    #         logger.info("Updating example configuration using %r", configData)
    #         #
    #         configD = {"version": 0.30, "created": datetime.datetime.now().isoformat(), "data": cD}
    #         if storeConfig:
    #             self.__mU.mkdir(configDirPath)
    #             self.__mU.doExport(configFilePath, configD, fmt="json", indent=3)
    #     except Exception as e:
    #         logger.exception("Failing with %s", str(e))
    #     return configD
    #     #
