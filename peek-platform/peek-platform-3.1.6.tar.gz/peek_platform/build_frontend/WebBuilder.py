import logging
from datetime import datetime

import os
from typing import List

import pytz

from peek_platform.build_frontend.FrontendBuilderABC import (
    FrontendBuilderABC,
    BuildTypeEnum,
)
from peek_platform.build_common.BuilderOsCmd import runNgBuild
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class WebBuilder(FrontendBuilderABC):
    def __init__(
        self,
        frontendProjectDir: str,
        platformService: str,
        jsonCfg,
        loadedPlugins: List,
    ):
        FrontendBuilderABC.__init__(
            self,
            frontendProjectDir,
            platformService,
            self._buildType(platformService),
            jsonCfg,
            loadedPlugins,
        )

        self.isField = "field" in platformService
        self.isOffice = "office" in platformService
        self.isAdmin = "admin" in platformService

    @staticmethod
    def _buildType(platformService: str):
        if "field" in platformService:
            return BuildTypeEnum.WEB_FIELD
        if "office" in platformService:
            return BuildTypeEnum.WEB_OFFICE
        if "admin" in platformService:
            return BuildTypeEnum.WEB_ADMIN

        raise NotImplementedError("Unknown build type")

    @deferToThreadWrapWithLogger(logger, checkMainThread=False)
    def build(self) -> None:
        if not self._jsonCfg.feWebBuildPrepareEnabled:
            logger.info(
                "%s SKIPPING, Web build prepare is disabled in config",
                self._platformService,
            )
            return

        excludeRegexp = (r".*__pycache__.*", r".*[.]py$")

        if self.isField:
            excludeRegexp += (
                r".*[.]dweb[.]ts$",
                r".*[.]dweb[.]html$",
                r".*[.]dweb[.]scss",
            )

        elif self.isOffice:
            excludeRegexp += (
                r".*[.]mweb[.]ts$",
                r".*[.]mweb[.]html$",
                r".*[.]mweb[.]scss",
            )

        elif self.isAdmin:
            pass

        else:
            raise NotImplementedError(
                "This is neither admin, field or office web"
            )

        self._dirSyncMap = list()

        feBuildDir = self._frontendProjectDir
        feBuildSrcDir = os.path.join(feBuildDir, "src")
        feBuildAssetsDir = os.path.join(feBuildDir, "src", "assets")
        feNodeModDir = os.path.join(feBuildDir, "node_modules")
        fePluginDir = os.path.join(feBuildSrcDir, "@_peek")
        fePrivatePluginDir = os.path.join(feBuildSrcDir, "@peek")
        feModuleDirs = [
            (fePrivatePluginDir, "moduleDir"),
        ]

        if not os.path.exists(fePluginDir):
            os.makedirs(fePluginDir)

        if not os.path.exists(fePrivatePluginDir):
            os.makedirs(fePrivatePluginDir)

        pluginDetails = self._loadPluginConfigs()

        # --------------------
        # Check if node_modules exists

        if not os.path.exists(os.path.join(feBuildDir, "node_modules")):
            raise NotADirectoryError(
                "%s node_modules doesn't exist, ensure you've run "
                "`npm install` in dir %s",
                self._platformService,
                feBuildDir,
            )

        # --------------------
        # Prepare the common frontend application

        # self.fileSync.addSyncMapping(feSrcAppDir, os.path.join(feBuildSrcDir, 'app'),
        #                              excludeFilesRegex=excludeRegexp)

        # --------------------
        # Prepare the home and title bar configuration for the plugins
        self._writePluginHomeLinks(fePluginDir, pluginDetails)
        self._writePluginTitleBarLinks(fePluginDir, pluginDetails)
        self._writePluginConfigLinks(fePluginDir, pluginDetails)

        # --------------------
        # Prepare the plugin lazy loaded part of the application
        self._writePluginAppRouteLazyLoads(fePluginDir, pluginDetails)
        self._syncPluginFiles(
            fePluginDir,
            pluginDetails,
            "appDir",
            excludeFilesRegex=excludeRegexp,
        )

        # --------------------
        # Prepare the plugin lazy loaded part of the application
        self._writePluginCfgRouteLazyLoads(fePluginDir, pluginDetails)
        self._syncPluginFiles(
            fePluginDir,
            pluginDetails,
            "cfgDir",
            isCfgDir=True,
            excludeFilesRegex=excludeRegexp,
        )

        # --------------------
        # Prepare the plugin assets
        self._syncPluginFiles(
            feBuildAssetsDir,
            pluginDetails,
            "assetDir",
            excludeFilesRegex=excludeRegexp,
        )

        # --------------------
        # Prepare the shared / global parts of the plugins

        self._writePluginRootModules(fePluginDir, pluginDetails)
        self._writePluginRootServices(fePluginDir, pluginDetails)
        self._writePluginRootComponents(fePluginDir, pluginDetails)

        for (
            feModDir,
            jsonAttr,
        ) in feModuleDirs:
            # Link the shared code, this allows plugins
            # * to import code from each other.
            # * provide global services.
            self._syncPluginFiles(
                feModDir,
                pluginDetails,
                jsonAttr,
                excludeFilesRegex=excludeRegexp,
            )

        # Lastly, Allow the clients to override any frontend files they wish.
        # Src Directory
        self.fileSync.addSyncMapping(
            self._jsonCfg.feFrontendSrcOverlayDir,
            fePluginDir,
            parentMustExist=True,
            deleteExtraDstFiles=False,
            excludeFilesRegex=excludeRegexp,
        )

        # node_modules Directory
        self.fileSync.addSyncMapping(
            self._jsonCfg.feFrontendNodeModuleOverlayDir,
            feNodeModDir,
            parentMustExist=True,
            deleteExtraDstFiles=False,
            excludeFilesRegex=excludeRegexp,
        )

        self.fileSync.syncFiles()

        if self._jsonCfg.feSyncFilesForDebugEnabled:
            logger.info(
                "%s starting frontend development file sync",
                self._platformService,
            )
            self.fileSync.startFileSyncWatcher()

        if self._jsonCfg.feWebBuildEnabled:
            logger.info("%s starting frontend web build", self._platformService)
            self._compileFrontend(feBuildDir)

    def _syncFileHook(self, fileName: str, contents: bytes) -> bytes:
        # replace imports that end with .dweb or .mweb to the appropriate
        # value
        # Otherwise just .web should be used if no replacing is required.

        for lineEnd in (os.linesep.encode(), (";" + os.linesep).encode()):

            if self.isField:
                contents = contents.replace(
                    b'.dweb"' + lineEnd, b'.mweb"' + lineEnd
                )

            elif self.isOffice:
                contents = contents.replace(
                    b'.mweb"' + lineEnd, b'.dweb"' + lineEnd
                )

            elif self.isAdmin:
                pass

            else:
                raise NotImplementedError("This is neither field or office web")

        if b"@Component" in contents:
            return self._patchComponent(fileName, contents)

        return contents

    def _patchComponent(self, fileName: str, contents: bytes) -> bytes:
        """Patch Component

        Apply patches to the WEB file to convert it to the NativeScript version

        :param fileName: The name of the file
        :param contents: The original contents of the file
        :return: The new contents of the file
        """
        inComponentHeader = False

        newContents = b""
        for line in contents.splitlines(True):
            if line.startswith(b"@Component"):
                inComponentHeader = True

            elif line.startswith(b"export"):
                inComponentHeader = False

            elif inComponentHeader:

                if self.isOffice:
                    line = (
                        line.replace(b".mweb.html", b".dweb.html")
                        .replace(b".mweb.css", b".dweb.css")
                        .replace(b".mweb.scss", b".dweb.scss")
                    )

                if self.isField:
                    line = (
                        line.replace(b".dweb.html", b".mweb.html")
                        .replace(b".dweb.css", b".mweb.css")
                        .replace(b".dweb.scss", b".mweb.scss")
                    )

            newContents += line

        return newContents

    def _compileFrontend(self, feBuildDir: str) -> None:
        """Compile the frontend

        this runs `ng build`

        We need to use a pty otherwise webpack doesn't run.

        """
        startDate = datetime.now(pytz.utc)
        hashFileName = os.path.join(feBuildDir, ".lastHash")

        if not self._recompileRequiredCheck(feBuildDir, hashFileName):
            logger.info(
                "%s Frontend has not changed, recompile not required.",
                self._platformService,
            )
            return

        logger.info(
            "%s Rebuilding frontend distribution", self._platformService
        )

        try:
            runNgBuild(feBuildDir)

        except Exception as e:
            if os.path.exists(hashFileName):
                os.remove(hashFileName)

            # Update the detail of the exception and raise it
            e.message = (
                "%s angular frontend failed to build." % self._platformService
            )
            raise

        logger.info(
            "%s frontend rebuild completed in %s",
            self._platformService,
            datetime.now(pytz.utc) - startDate,
        )
