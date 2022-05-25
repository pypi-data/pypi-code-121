"""
This module adapts 'isystem.test' winIDEA functionality to Python.
"""

from __future__ import print_function

import os
import sys
import shutil
import importlib
import subprocess as sproc
import traceback
# from typing import List

import isystem.connect as ic
import isystem.icutils

XSLT_BUILT_IN_PREFIX = '<built-in>'
DEFAULT_XSLT = XSLT_BUILT_IN_PREFIX + " isystemTestReport.xslt"
BLUE_CSS = XSLT_BUILT_IN_PREFIX + " blue.css"
GRAY_CSS = XSLT_BUILT_IN_PREFIX + " gray.css"

try:
    input = raw_input  # to work in Python 2 and Python 3
except NameError:
    pass


def connectToPrimaryCore(envConfig, winIDEAWorkspace, winIDEAId, pathToIConnectDll=''):
    """
    Connects to primary core in multicore targets.
    """

    loggingParams = ic.StrVector()
    envConfig.getLoggingParameters(loggingParams)

    isUseWinIDEAId = True
    if winIDEAId is None:
        isUseWinIDEAId = False
        winIDEAId = ""

    primaryCoreId = envConfig.getPrimaryCoreId()

    mccMgr = ic.CMulticoreConnectionMgr()
    mccMgr.connectPrimaryCore(loggingParams,
                              winIDEAWorkspace,
                              isUseWinIDEAId,
                              winIDEAId,
                              primaryCoreId,
                              pathToIConnectDll)
    return mccMgr


def getISysDirs(mccMgr, iyamlFileName, testBench):
    """
    Returns class containing directories used by winIDEA and testIDEA.
    """
    reportCfg = testBench.getTestReportConfig(True)
    reportFile = reportCfg.getFileName()

    workingDir = os.getcwd()
    iyamlFileNameAbs = os.path.join(workingDir, iyamlFileName)

    iyamlDir = os.path.split(iyamlFileNameAbs)[0]
    reportFileAbs = os.path.join(iyamlDir, reportFile)

    reportDir = os.path.split(reportFileAbs)[0]

    ideCtrl = mccMgr.getCIDEController('')

    winIDEAWsDir = ideCtrl.getPath(ic.CIDEController.WORKSPACE_DIR)

    winIDEAExeDir = ideCtrl.getPath(ic.CIDEController.WINIDEA_EXE_DIR)
    dotExeDir = os.path.join(winIDEAExeDir, 'graphwiz/bin')

    dirs = ISysDirs(winIDEAWsDir, iyamlDir, reportDir, dotExeDir)
    return dirs


def getXsltFName(reportConfig):
    """
    Returns name of XSLT as defined in the given reportConfig.
    """
    xsltFileName = reportConfig.getSelectedXsltFileName()

    if xsltFileName.startswith(XSLT_BUILT_IN_PREFIX):
        xsltFileName = xsltFileName[len(XSLT_BUILT_IN_PREFIX):].strip()

        reportFName = reportConfig.getAbsReportFileName()
        reportDir = os.path.split(reportFName)[0]
        return os.path.join(reportDir, xsltFileName)

    return xsltFileName


def createHtmlReport(mccMgr, reportConfig):
    """
    Creates test report in HTML format. Returns name of created HTML
    file, or None if file was not created because of settings in
    reportConfig.
    """
    outputFormat = reportConfig.getOutputFormat()

    if outputFormat != ic.CTestReportConfig.FMT_XML:
        return None

    if not reportConfig.isCreateHtml():
        return None

    xmlFName = reportConfig.getAbsReportFileName()

    if not xmlFName:
        return None

    htmlFName = os.path.splitext(xmlFName)[0] + ".html"

    javaApp, saxonJar = getSaxonPaths(mccMgr)

    # Example of expected cmd:
    # java -cp ../../../../branches/tableEditor/Eclipse/testidea/si.isystem.itest.p
    # lugin.core/lib/saxon9he.jar net.sf.saxon.Transform -s:reportFull.xml -a:on -o:saxtest.html
    # XSLT file name is built into exported xml file.
    cmd = javaApp + ' -cp ' + saxonJar + ' net.sf.saxon.Transform -s:' + \
          xmlFName + ' -a:on -o:' + htmlFName
    try:
        sproc.check_call(cmd)
    except Exception as ex:
        print(cmd)
        raise ex

    return htmlFName

# add types when we'll get rid of Python 2.7
def exportForCobertura(mccMgr, #: ic.CMulticoreConnectionMgr,
                       coreId, #: str,
                       trdFilePath, #: str,
                       srcDirs, #: List[str] = [],
                       isIndent = False):
    """
    This function exports the given trd file in iSYSTEM XML
    coverage format to current working dir. If Jenkins is running the
    test, then current working dir is Jenkins workspace dir.

    @param mccMgr connection manager used to export coverage from winIDEA
    @param trdFilePath name of trd file to be exported. It is also used
           for the name of output file, with extension '.cobertura.xml' added.
    @param srcDirs if specified, the <sources> tag is added to the exported XML.
           Each item in the list creates one <source> tag. Use this feature
           if analysis tool needs to locate the sources, for example GitLab
           coverage analysis.
    @param isIndent if True, the output XML is created with newlines and
           indentations. Good for readability, but files are bigger.
    """

    # get paths
    _, trdFName = os.path.split(trdFilePath)

    coverage = ic.CCoverageController2(mccMgr.getConnectionMgr(coreId),
                                       trdFilePath, 'r')
    coverage.waitUntilLoaded()

    # export xml to current working dir (= Jenkins workspace dir)
    currentDir = os.getcwd()
    isysExportForCoberturaFName = trdFName + '.isysCvrg.xml'
    isysExportForCoberturaFPath = os.path.join(currentDir, isysExportForCoberturaFName)

    exportCfg = ic.CCoverageExportConfig()
    exportCfg.setFileName(isysExportForCoberturaFPath) \
             .setExportModuleLines(False) \
             .setExportSources(False) \
             .setExportFunctionLines(True) \
             .setExportAsm(False) \
             .setExportRanges(False)

    coverage.exportData(exportCfg)

    # Current dir is the one where script is started from. When started
    # from Jenkins, current dir is Jenkins workspace dir.

    # run saxon
    # Example of expected cmd:
    # java -jar /c/ISYSTEM_APPS/saxon9he/saxon9he.jar -s:func4.xml -xsl:isysCvrgToCobertura.xslt
    # -o:cobertura.xml '!indent=yes'
    #
    # Example when run from Jenkins:
    # C:\winIDEA\2012\jre\bin\java.exe -jar C:\winIDEA\2012\saxon9he.jar
    #   -s:test-1.trd.isysCvrg.xml
    #   -xsl:d:\apps\Python33\lib\site-packages\isystem\isysCvrgToCobertura.xslt
    #   -o:test-1.trd.cobertura.xml
    javaApp, saxonJar = getSaxonPaths(mccMgr)

    scriptDir = os.path.dirname(__file__)
    xsltFPath = os.path.join(scriptDir, ic.CVRG_TO_COBERTURA_XSLT_FNAME)
    # should appear in Jenkins workspace (current working dir)
    coberturaXmlFName = trdFName + '.cobertura.xml'

    cmd = javaApp + ' -jar ' + saxonJar + ' -s:' + isysExportForCoberturaFName + \
          ' -xsl:' + xsltFPath + ' -o:' + coberturaXmlFName

    if srcDirs:
        cmd += ' "srcDirs=' + ':'.join(srcDirs) + '"'
    
    if isIndent:
        cmd += ' !indent=yes'

    try:
        sproc.check_call(cmd)
    except Exception as ex:
        print(cmd)
        raise ex


def getSaxonPaths(mccMgr):
    """ Returns paths of java.exe and saxon distributed with winIDEA. """
    ideCtrl = mccMgr.getCIDEController('')
    winIDEAExeDir = ideCtrl.getPath(ic.CIDEController.WINIDEA_EXE_DIR)
    javaApp = os.path.join(winIDEAExeDir, 'jre', 'bin', 'java.exe')
    saxonJar = os.path.join(winIDEAExeDir, 'saxon9he.jar')

    if not os.path.exists(saxonJar):
        saxonJar = '/ISYSTEM_APPS/saxon9he/saxon9he.jar'

    return javaApp, saxonJar


def _isSameFile(path1, path2):
    return  (os.path.normcase(os.path.abspath(path1)) ==
             os.path.normcase(os.path.abspath(path2)))


def _copyResource2ReportDir(resourceFileName, reportFileName, isEmbedXsltCss):

    srcDir = os.path.dirname(__file__) # dir of this script = isystem module,
                                       # where css and xslt are located
    destDir = os.path.dirname(reportFileName)

    if not resourceFileName:
        raise ValueError("'resouceFileName' must not be empty!")

    # remove prefix for stylesheet files built into testIDEA
    if resourceFileName.startswith(XSLT_BUILT_IN_PREFIX):
        resourceFileName = resourceFileName[len(XSLT_BUILT_IN_PREFIX):].strip();
        destFile = os.path.join(destDir, resourceFileName)

        srcResourceFileName = os.path.join(srcDir, resourceFileName)

        if isEmbedXsltCss:
            srcResourceFileName += ic.TMP_XSLT_CSS_EXTENSION
            destFile += ic.TMP_XSLT_CSS_EXTENSION

        if not os.path.exists(srcResourceFileName):
            raise Exception("Tests were executed, and report weas saved, but " + \
                            "there is no resource file '" + srcResourceFileName +
                            "' in isystem module for viewing reports in browser. ")

        if not os.path.exists(destFile) or not _isSameFile(destFile, srcResourceFileName):
            shutil.copyfile(srcResourceFileName, destFile)
    else:
        raise ValueError("Only resources provided by isystem module can be copied by this function!")


def copyXsltAndCss(reportConfig):
    # copy XSLT and CSS from dir of this script to report dir, but
    # only if they are built-in files. For user created XSLT and/or CSS
    # users have to take care - either specify abs path or copy manually
    reportFileName = reportConfig.getFileName()
    isEmbedXsltCss = reportConfig.isEmbedXsltCss()

    xsltFileName = reportConfig.getSelectedXsltFileName();
    _copyResource2ReportDir(xsltFileName, reportFileName, isEmbedXsltCss)

    cssFileName = reportConfig.getCssFile()
    _copyResource2ReportDir(cssFileName, reportFileName, isEmbedXsltCss)


class ISysDirs:
    """
    This class contains directories used by iSYSTEM tools:
    winIDEAWorkspaceDir, iyamlDir, reportDir, and dotExeDir (dir of dot tool).
    """
    def __init__(self, winIDEAWorkspaceDir, iyamlDir, reportDir, dotExeDir):
        self.winIDEAWorkspaceDir = winIDEAWorkspaceDir
        self.iyamlDir = iyamlDir
        self.reportDir = reportDir
        self.dotExeDir = dotExeDir

    def getWinIDEAWorkspaceDir(self):
        """
        Returns directory of winIDEA workspace (*.xjrf) file currently
        opened in winDEA.
        """
        return self.winIDEAWorkspaceDir

    def getIyamlDir(self):
        """ Returns directory where iyaml file with test cases is located. """
        return self.iyamlDir

    def getReportDir(self):
        """ Returns directory where test report file will be saved. """
        return self.reportDir

    def getDotExeDir(self):
        """ Returns directory where graphwiz tools bundled with winIDEA are located. """
        return self.dotExeDir


class PTestCase:
    """
    This class is a wrapper of 'ic.CTestCase' class. It
    has the same functionality, but adapted to Python. The only
    difference is in handling of callbacks specified in test
    specification (stubs, 'initFunc', 'endFunc', ...). While
    'ic.CTestCase' requires C++ implementation of these
    methods, this class can call methods defined in Python.  All
    callback methods must be defined in object passed as parameter
    'extensionObj' to methods in this class.

    Parameters:
    icConnection - instance of CMulticoreConnectionMgr. For backward
                   compatibility also instance of ICFactory or
                   ConnectionMgr is accepted, but some functionality
                   does not work in that case.
                   ICFactory and ConnectionMgr are deprecated
                   since 9.12.188, 2014-09-05
    """

    def __init__(self, icConnection):

        if isinstance(icConnection, isystem.icutils.ICFactory):
            self.connectionMgr = icConnection.getConnectionMgr()
        elif isinstance(icConnection, ic.ConnectionMgr):
            self.connectionMgr = icConnection
        elif isinstance(icConnection, ic.CMulticoreConnectionMgr):
            self._mccMgr = icConnection
            self.connectionMgr = None
        else:
            raise Exception('Parameter should be of type ICFactory or ConnectionMgr!')

        self._cTestCase = None
        self._resultContainer = ic.CTestReportContainer()
        self._isRunningDerivedTests = False
        self._testCaseInitConfig = None
        self._initTargetForTestCaseTimeout = 30000 # 30 seconds
        self._testBatchStateMap = {}
        self._isMeasureStackUsage = False
        self._testGlobalTimeout = 0
        self._envConfig = None
        self._isysDirs = ISysDirs('', '', '', '')


    def setISysDirs(self, isysDirs):
        """ Sets directories used to access files. """
        self._isysDirs = isysDirs


    def initEnvironment(self, testEnvConfig, dbg, ideCtrl, targetStopTimeout):
        """
        Deprecated since 9.12.188, 2014-09-05, call executeInitSequence() instead.

        Initializes target, according to settings in testEnvConfig.

        Parameters:

        testEnvConfig: instance of ic.CTestEnvironmentConfig
        """
        ic.CTestBench.initTargetForTest(testEnvConfig,
                                        dbg,
                                        ideCtrl,
                                        targetStopTimeout)

        stackUsageCfg = testEnvConfig.getStackUsageConfig(True)
        self._isMeasureStackUsage = ((not stackUsageCfg.isEmpty())  and
                                     stackUsageCfg.isActive())
        self._testGlobalTimeout = testEnvConfig.getTestTimeout()


    def _initSequenceLoop(self, envConfig, multicoreCMgr, targetStopTimeout, monitor):
        initSeq = envConfig.getTestBaseList(ic.CTestEnvironmentConfig.E_SECTION_INIT_SEQUENCE,
                                            True)
        numInitSteps = initSeq.size()
        for stepIdx in range(numInitSteps):
            action = ic.CInitSequenceAction.cast(initSeq.get(stepIdx))
            coreId = self._getConfiguredCoreID(action.getCoreId())

            if monitor != None  and  hasattr(monitor, "initAction"):
                monitor.initAction(action.getActionName())

            if action.getAction() == ic.CInitSequenceAction.EIACallScriptFunction:
                params = ic.CSequenceAdapter(action,
                                             ic.CInitSequenceAction.E_INIT_SEQ_PARAMS,
                                             True)
                if params.size() == 0:
                    raise Exception("Missing script function name in init sequence!\n" +
                                    'actionName:' + action.getActionName() + '\n' +
                                    'actionIdx: ' + stepIdx + '\n' +
                                    'coreId: ' + coreId)

                functionName = params.getValue(0)
                scriptParams = ic.StrVector()

                for idx in range(1, params.size()):
                    scriptParams.push_back(params.getValue(idx))

                self._callScriptFunction(None, functionName, scriptParams,
                                         extensionObj, "")
            else:
                ic.CTestBench.executeInitAction(envConfig,
                                                multicoreCMgr,
                                                action,
                                                stepIdx,
                                                True,
                                                targetStopTimeout)


    def executeInitSequence(self,
                            envConfig,
                            multicoreCMgr,
                            targetStopTimeout,
                            extensionObj,
                            monitor):
        """
        Initializes target, according to settings in envConfig.

        Parameters:

        envConfig: instance of ic.CTestEnvironmentConfig
        multicoreCMgr: CMulticoreConnectionMgr, may not be None
        targetStopTimeout: timeout in milliseconds
        extensionObj: object with script extension methods. May be None
                      only if init sequence contains no script actions.
        monitor: object to provide feedback to the user. May be set to None.
        """

        self._envConfig = envConfig

        stackUsageCfg = envConfig.getStackUsageConfig(True)
        self._isMeasureStackUsage = ((not stackUsageCfg.isEmpty())  and
                                     stackUsageCfg.isActive())

        self._testGlobalTimeout = envConfig.getTestTimeout()

        if envConfig.isAlwaysRunInitSeqBeforeRun():
            self._initSequenceLoop(envConfig, multicoreCMgr, targetStopTimeout, monitor)

        # see comment in Java source
        dataCtrl = multicoreCMgr.getCDataController2("")
        ic.CTestBench.configureStackUsage(dataCtrl, envConfig, "") # see comments in Java
        self._configBPMode(envConfig, multicoreCMgr, False)


    def _configBPMode(self, envConfig, multicoreCMgr, isBeforeInit):
        coreIds = ic.StrVector()
        envConfig.getCoreIds(coreIds)
        if not coreIds:
            coreIds = [""]
        coreIdx = 0
        for coreId in coreIds:
            ideCtrl = multicoreCMgr.getCIDEController(coreId)
            print("bpType: ", envConfig.getBreakpointType(), isBeforeInit)
            ic.CTestBench.configureBreakpointsMode(ideCtrl, envConfig.getBreakpointType(),
                                                   coreIdx, isBeforeInit)
            connectionMgr = multicoreCMgr.getConnectionMgr(coreId)
            ic.CTestCaseController.clearAllTests(connectionMgr)
            coreIdx += 1


    def restoreEnvironment(self,
                           testEnvConfig,
                           dbg=None,
                           ideCtrl=None,
                           targetStopTimeout=0):
        """
        Deprecated since 9.12.188, 2014-09-05. Use restoreState() instead.

        Restores target after test, according to settings in testEnvConfig.

        Parameters:

        testEnvConfig: instance of ic.CTestEnvironmentConfig
        Other parameters are ignored and deprecated - will be removed in future
        versions.
        """

        ic.CTestBench.restoreTargetAfterTest(testEnvConfig,
                                             dbg,
                                             ideCtrl,
                                             targetStopTimeout)
        self._isMeasureStackUsage = False
        self._testGlobalTimeout = 0


    def restoreState(self):
        """
        Restores internal variables after test
        """

        self._isMeasureStackUsage = False
        self._testGlobalTimeout = 0


    def setTestCaseInitConfig(self, testCaseInitConfig):
        """
        Call this method with instance of CTestCaseTargetInitConfig
        (see class CTestBench), if you want to initialize target
        before each test case.
        """
        self._testCaseInitConfig = testCaseInitConfig


    def runTests(self,
                 testSpec,
                 extensionObj=None,
                 monitor=None,
                 testFilter=None,
                 isDebugMode=False,
                 envConfig=None,
                 testBench=None):
        """
        This method runs the given test specification and derived test
        specifications.

        Parameters:

        testSpec: test specification as string in YAML format or instance of
                           ic.CTestSpecification. See User's guide for
                           detailed description of YAML syntax.

        extensionObj: object, with functions, which are specified in test
                       specification sections 'initFunc', 'endFunc', 'initTargetFunc',
                       'restoreTargetFunc', and 'stubs.script'.
                       If test specification does not contain these
                       sections, this parameter may be set to None.

        monitor: object to be notified about test progress. It has to implement
                 the following methods:
                   isCanceled(self) should return \\c True if you want to cancel tests in
                                progress, \\c False otherwise
                   subTask(self, string) this method is called when the test starts. Parameter
                                   contains test ID and function name as string.
                   worked(self, int) this method is called when the test completes. Parameter
                               is always one, which means one test has completed.
                 Optional method:
                   setTestInfo(self, **kwargs) parameter 'testCase' contains current
                                               CTestSpecification object


        isDebugMode: when True, cleanup is not performed immediately after error, but
                     waits for the user to press ENTER. This way we can see winIDEA
                     state in case of an error during test, for example when it stops
                     on some forgotten breakpoint, or when we stop the target because
                     it is inside never ending or long running loop.

        testFilter: instance of class CTestFilter, if we want to execute only subset
                    of the given tests. If None, all tests are executed. If specified,
                    make sure to call \c testSpec.clearMergedFilterInfo(True) before
                    calling this method, otherwise stale cache filtering data might
                    cause strange behavior of filter.
        envConfig: instance of class CTestEnvironmentConfig. Should never be null.
                   For backward compatibility null is tolerated, but interrupts
                   on target are not disabled in that case!
        """

        self.runDerivedTests(testSpec, extensionObj, monitor, testFilter,
                             isDebugMode, envConfig, testBench)


    def itest(self, testSpec, extensionObj, isDebugMode=False, hostVars=None, filterCtrl=None):
        """
        This method executes unit test according to the given test
        specification. Only the given test specification is executed
        - no merging is performed and derived test specifications are NOT
        executed.
        If you want to execute also derived tests, it is more effectively
        to call method runTests(), since some optimization may be performed
        in unit tests.

        Parameters:

        testSpec: test specification as string in YAML format or instance of
                           ic.CTestSpecification. See User's guide for
                           detailed description of YAML syntax.

        extensionObj: object, with functions, which are specified in test
                       specification sections 'initFunc', 'endFunc', 'initTargetFunc',
                       'restoreTargetFunc', and 'stubs.script'.
                       If test specification does not contain these
                       sections, this parameter may be set to None.

        hostVars: Should be None or instance of CTestHostVars. If test case contains
                  host variables, they should be defined in this object.

        isDebugMode: when True, cleanup is not performed immediately after error, but
                     waits for the user to press ENTER. This way we can see winIDEA
                     state in case of an error during test, for example when it stops
                     on some forgotten breakpoint, or when we stop the target because
                     it is inside never ending or long running loop.

        filterCtrl: may be None if coverage merge (section Analyzer / Coverage)
                    is not used in the given test case. If coverage merge is
                    specified, then this parameter must not be None and symbols must be
                    initialized. Example:

                    testBench = ic.CTestBench()

                    # If running multicore tests, set core IDs:
                    #   testEnv = testBench.getTestEnvironmentConfig(True)
                    #   testEnv.setTagValue(ic.CTestEnvironmentConfig.E_SECTION_CORE_IDS,
                    #                       '[core-0, core1]')

                    testBench.refreshSymbolsAndGroupsIfEmpty(mccMgr, None)
                    filterCtrl = testBench.getFilterController()
        """

        if not isinstance(testSpec, ic.CTestSpecification):
            testSpec = self._createTestSpecification(testSpec)

        if not hostVars:
            hostVars = ic.CTestHostVars()

        hostVars.initTestCaseVars(testSpec, None)
        analyzerFilesToMerge = self._getFilesForCvrgMerge(testSpec,
                                                          filterCtrl,
                                                          extensionObj)

        coreId = self._getConfiguredCoreID(testSpec.getCoreId())
        isTestBatchOn = self._testBatchStateMap.get(coreId)
        if isTestBatchOn is None:
            isTestBatchOn = False

        diffs = self._itest(testSpec, testSpec, extensionObj, hostVars,
                            analyzerFilesToMerge,
                            isTestBatchOn,
                            isDebugMode)

        if self._testBatchStateMap.get(coreId):
            self._cTestCase.getTestController().setTestBatchNS(False)
            self._testBatchStateMap[coreId] = False

        return diffs


    def _itest(self, testSpec, mergedTestSpec, extensionObj, hostVars,
               analyzerFilesToMerge,
               isTestBatchOn,
               isDebugMode=False,
               monitor=None):

        if not mergedTestSpec.getRunFlag():
            return []

        # if this method is called directly by client, not runDerivedTests(),
        # clear results here.
        if not self._isRunningDerivedTests:
            self._resultContainer = ic.CTestReportContainer()

        coreId = self._getConfiguredCoreID(mergedTestSpec.getCoreId())
        connectionMgr = self._getCMgr(coreId)
        self._cTestCase = ic.CTestCase(connectionMgr, hostVars)

        # initialize target if required
        initTargetFunction = mergedTestSpec.getInitTargetFunction(True)
        if isTestBatchOn  and  initTargetFunction.getName():
            # if user defined init target function, this function may execute operation, which
            # invalidates caching of registers (download, reset, ...). To prevent itest error
            # in such cases, always restore the registers before calling this script function.
            # Another solution would be additional config. item for storing registers in iyaml, but
            # this would be hard to understand option exposing testIDEA internals.
            ic.CTestCaseController.setTestBatch(connectionMgr, False)
            isTestBatchOn = False

        scriptInitTarget = self._callCTestFunction(mergedTestSpec,
                                                   self._cTestCase.getHostVars(),
                                                   ic.CTestResultBase.SE_INIT_TARGET,
                                                   initTargetFunction,
                                                   extensionObj)

        scriptResultsList = []

        try:
            isTestBatchOn = self._cTestCase.runTest_init_target(mergedTestSpec,
                                                                isDebugMode,
                                                                isTestBatchOn)
            self._testBatchStateMap[coreId] = isTestBatchOn
            testCaseCtrl = self._cTestCase.getTestController()

            # This method may block, if target does not stop. See Java for
            # impl. of this method, which accepts user input.
            # Since this method blocks in native call, GIL is also locked. If
            # this is problem in multithreaded apps., copy and adapt this method from
            # Java code, or contact iSYSTEM support: support@isystem.com
            self._cTestCase.runUntilStopPoint(mergedTestSpec.getBeginStopCondition(True),
                                              mergedTestSpec.getTestId())

            testCaseTimeout = mergedTestSpec.getTestTimeout()
            if testCaseTimeout == -1:
                testCaseTimeout = self._testGlobalTimeout

            self._cTestCase.runTest_init_test(True,
                                              self._isMeasureStackUsage,
                                              testCaseTimeout)

            if self._cTestCase.getTestResults().isPreConditionError():
                return []

            try:
                self._initExtensionObj(extensionObj, testCaseCtrl)

                scriptInitFunc = self._callCTestFunction(mergedTestSpec,
                                                         self._cTestCase.getHostVars(),
                                                         ic.CTestResultBase.SE_INIT_FUNC,
                                                         mergedTestSpec.getInitFunction(True),
                                                         extensionObj)
                self._cTestCase.runTest_exec_begin()
                isResumeCoverage = False
                isStubOrTestPoint = False

                while True:
                    self._cTestCase.runTest_exec_loopStart(mergedTestSpec,
                                                           isResumeCoverage,
                                                           isStubOrTestPoint)

                    # wait for stop or user cancel, 1s timeout for unit tests
                    while not self._cTestCase.runTest_exec_waitForStop(mergedTestSpec, 1000):
                        # if user can cancel test execution, put code here
                        pass

                    isStubOrTestPoint = self._runTest_exec_langSpecific(mergedTestSpec,
                                                                        extensionObj,
                                                                        scriptResultsList)
                    isResumeCoverage = True

                    if not isStubOrTestPoint:
                        break

                self._cTestCase.runTest_exec_end()

                scriptEndFunc = self._callCTestFunction(mergedTestSpec,
                                                        self._cTestCase.getHostVars(),
                                                        ic.CTestResultBase.SE_END_FUNC,
                                                        mergedTestSpec.getEndFunction(True),
                                                        extensionObj)

                differences = ic.StrVector()
                self._cTestCase.runTest_finalize(differences, False, analyzerFilesToMerge)
            except Exception:
                if isDebugMode:
                    input("Error in test execution! Press ENTER to continue with cleanup ...")
                    self._cTestCase.handleException()
                    self._cTestCase.clearTest() # skipped in C++ code in debug mode
                else:
                    self._cTestCase.handleException()

                if isTestBatchOn:
                    # toggle to restore registers in case of exception
                    self._cTestCase.getTestController().setTestBatchNS(False)
                    self._cTestCase.getTestController().setTestBatchNS(True)

                # Persistent vars must be deleted regardless of test cases result,
                # even if test case fails because function under test is not found.
                # This makes test execution more robust - for example, if function
                # was removed or renamed, persist vars must be deleted even if test
                # init fails, otherwise next test case may also fail if it creates
                # persist var with the same name.
                self._cTestCase.deletePersistentVars(testSpec.getPersistentVars(True))

                raise

            self._cTestCase.deletePersistentVars(testSpec.getPersistentVars(True))

            self._getResults_langSpecific(testSpec,
                                          mergedTestSpec,
                                          extensionObj,
                                          scriptInitTarget,
                                          scriptInitFunc,
                                          scriptResultsList,
                                          scriptEndFunc,
                                          monitor)

            pyDiffs = []
            pyDiffs.extend(differences)
            return pyDiffs

        except Exception:

            # see comment for 'deletePersistentVars()' above
            self._cTestCase.deletePersistentVars(testSpec.getPersistentVars(True))

            if not self._isRunningDerivedTests:
                exMsg = traceback.format_exc()
                result = ic.CTestResult(mergedTestSpec, exMsg)
                # use pointer value of the non-merged test spec as mapping key
                self._resultContainer.putTestResult(testSpec, result)
            else:
                raise

        return []


    def _runTest_exec_langSpecific(self,
                                   testSpec,
                                   extensionObj,
                                   stubScriptResults):

        itestCaseCtrl = self._cTestCase.getTestController()
        status = itestCaseCtrl.getStatus()
        isTestPoint = False

        self._cTestCase.waitForAnalyzerToDownloadData()

        if status == ic.IConnectTest.stateStub:
            stubScriptResults.append(self._callStubs(testSpec, itestCaseCtrl,
                                                     testSpec.getStubs(True),
                                                     extensionObj))
            return True
        elif status == ic.IConnectTest.stateUnexpectedStop:
            isTestPoint, scriptResult = self._execTestPoints(testSpec,
                                                             itestCaseCtrl,
                                                             extensionObj)
            stubScriptResults.append(scriptResult)

            self._cTestCase.isSystemTestStopOnBP()

            return isTestPoint

        elif status == ic.IConnectTest.stateException:
            self._cTestCase.setTargetException(True)

        return False


    def _getResults_langSpecific(self,
                                 testSpec,
                                 mergedTestSpec,
                                 extensionObj,
                                 scriptInitTarget,
                                 scriptInitFunc,
                                 scriptResultsList,
                                 scriptEndFunc,
                                 monitor):

        testResult = self._cTestCase.getTestResults(mergedTestSpec)

        scriptRestoreTarget = self._callCTestFunction(mergedTestSpec,
                                                      self._cTestCase.getHostVars(),
                                                      ic.CTestResultBase.SE_RESTORE_TARGET,
                                                      mergedTestSpec.getRestoreTargetFunction(True),
                                                      extensionObj)

        self._setScriptResult(testResult, scriptInitTarget)
        self._setScriptResult(testResult, scriptInitFunc)

        for stubErrInfoList in scriptResultsList:
            self._setScriptResult(testResult, stubErrInfoList)

        self._setScriptResult(testResult, scriptEndFunc)
        self._setScriptResult(testResult, scriptRestoreTarget)

        self._drawDiagrams(mergedTestSpec, testResult, monitor)

        self._resultContainer.putTestResult(testSpec, testResult)



    def _setScriptResult(self, cResult, scriptResult):

        if scriptResult:
            funcType = scriptResult[0]
            funcInfo = scriptResult[1]
            funcOutList = scriptResult[2]

            if funcInfo:
                cResult.appendScriptOutput(funcType, funcInfo)

            if funcOutList:
                cResult.appendScriptError(funcType, funcOutList)


    def _drawDiagrams(self, testSpec, testResult, monitor):

        diagrams = testSpec.getDiagrams(True)
        if diagrams.isActive() != ic.E_TRUE:
            return

        # currently there is no timeout, as scripts should be written so that
        # they always return.
        self._createDiagrams(testSpec, testResult, monitor)


    def _createDiagrams(self, testSpec, testResult, monitor):

        diagrams = testSpec.getDiagrams(True)
        diagConfigsList = diagrams.getConfigurations(True)
        numDiagConfigs = diagConfigsList.size()
        for idx in range(0, numDiagConfigs):
            diagConfig = ic.CTestDiagramConfig.cast(diagConfigsList.get(idx))

            if diagConfig.isActive() == ic.E_TRUE:
                self._createDiagram(testSpec,
                                    diagConfig,
                                    testResult,
                                    monitor)


    def _createDiagram(self, testSpec, diagConfig, testResult, monitor):

        reportDir = self._isysDirs.getReportDir()
        outFile = ic.CTestHostVars.getDiagramFileName(testSpec, diagConfig)
        outFile = os.path.join(reportDir, outFile)

        # delete output file first, to prevent outdated images being shown and
        # included in reports in case of silent script error (empty except block,
        # for example)

        if os.path.exists(outFile):
            os.remove(outFile)

        diagType = diagConfig.getDiagramType()

        # if (diagType == ic.CTestDiagramConfig.ECallGraph  or
        #     diagType == ic.CTestDiagramConfig.ESequenceDiagram):

        #     if not os.path.exists(ic.CTestDiagramConfig.SEQ_AND_CALL_DIAG_PY):
        #         raise Exception("Script '" + ic.CTestDiagramConfig.SEQ_AND_CALL_DIAG_PY +
        #                         "' not found. " +
        #                         "Please run test case at least once from testIDEA!")

        # elif diagType == ic.CTestDiagramConfig.EFlowChart:

        #     if not os.path.exists(ic.CTestDiagramConfig.FLOW_CHART_PY):
        #         raise Exception("Script '" + ic.CTestDiagramConfig.FLOW_CHART_PY +
        #                         "' not found. " +
        #                         "Please run test case at least once from testIDEA!")

        dotExeDir = self._isysDirs.getDotExeDir()

        profilerExportFile = ""
        if testResult:
            profilerExportFile = testResult.getProfilerExportFileName()

        cmdLineArgs = ic.StrVector()
        diagConfig.getScriptCmdLineArgs(testSpec, outFile,
                                        profilerExportFile,
                                        dotExeDir, cmdLineArgs)

        if monitor != None:
            monitor.diagram(' '.join(cmdLineArgs))

        if diagType == ic.CTestDiagramConfig.ECustomAsync:
            self._createDiagramWithScriptAsync(cmdLineArgs)
        else:
            self._createDiagramWithScript(cmdLineArgs)


    def _createDiagramWithScript(self, cmdLineArgs):
        moduleName = cmdLineArgs[0]
        diagramModule = importlib.import_module(moduleName)
        # remove module name from args as expected by main()
        diagramModule.main(cmdLineArgs[1:])


    def _createDiagramWithScriptAsync(self, cmdLineArgs):
        cmdLineArgsAsList = list(cmdLineArgs)
        cmdLineArgsAsList.insert(0, sys.executable)
        sproc.Popen(cmdLineArgsAsList)


    def _initExtensionObj(self, extensionObj, testCaseCtrl):
        if extensionObj != None:
            # tests started from Python have access to the same testCaseCtrl
            # as used by the script, but this is not available for testIDEA - it
            # is not possible to pass object pointers between applications
            extensionObj._isys_testCaseController = testCaseCtrl
            # the handle is available to both, Python apps and testIDEA.
            extensionObj._isys_testCaseHandle = testCaseCtrl.getTestCaseHandle()


    def _getConfiguredCoreID(self, coreId):
        if not coreId  and  self._envConfig != None:
            return self._envConfig.getPrimaryCoreId()
        return coreId


    def runDerivedTests(self,
                        testSpec,
                        extensionObj=None,
                        monitor=None,
                        testFilter=None,
                        isDebugMode=False,
                        envConfig=None,
                        testBench=None):
        """
        Deprecated! Clients should use method runTests() instead!
        """
        if isinstance(testSpec, ic.CTestSpecification):
            testSpec = testSpec
        else:
            testSpec = self._createTestSpecification(testSpec)

        self._envConfig = envConfig
        filterController = None

        # reset results
        if testBench != None:  # backward compatibility (pre 9.12.269)
            self._resultContainer = testBench.getTestReportContainer()
            self._resultContainer.clearResults()
            filterController = testBench.getFilterController()
        else:
            self._resultContainer = ic.CTestReportContainer()

        self._isRunningDerivedTests = True

        _interruptStates = ic.StrStrMap()
        # coreId = self._getConfiguredCoreID(testSpec.getCoreId())
        # testCtrl = ic.CTestCaseController(self._getCMgr(coreId), 0)

        self._configureHostVars(self._isysDirs, envConfig)

        try:
            if envConfig != None: # check because of backward compatibility (before 9.12.188)
                ic.CTestBench.configureInterrupts(envConfig,
                                                  self._mccMgr,
                                                  _interruptStates)

            if testBench != None:  # backward compatibility (pre 9.12.269)
                self._runGroupScripts(testBench.getGroup(True),
                                      ic.CTestGroup.E_SECTION_GROUP_INIT_SCRIPT,
                                      ic.CTestResultBase.SE_GROUP_INIT_FUNC,
                                      envConfig, monitor, extensionObj)

            self._runTestsRecursive(testSpec, extensionObj,
                                    monitor,
                                    filterController,
                                    testFilter, isDebugMode)

            if envConfig != None: # check because of backward compatibility (before 9.12.188)
                ic.CTestBench.restoreInterrupts(envConfig,
                                                self._mccMgr,
                                                _interruptStates)

                if testBench != None:  # backward compatibility (pre 9.12.269)
                    testBench.calculateGroupResults(self._mccMgr, envConfig)
                    self._runGroupScripts(testBench.getGroup(True),
                                          ic.CTestGroup.E_SECTION_GROUP_END_SCRIPT,
                                          ic.CTestResultBase.SE_GROUP_END_FUNC,
                                          envConfig, monitor, extensionObj)

        finally:
            self._isRunningDerivedTests = False
            try:
                # if flag is ON from the last test, restore registers
                coreIds = ic.StrVector()
                if self._envConfig:
                    self._envConfig.getCoreIds(coreIds)
                else:
                    coreIds.append('')

                for coreId in coreIds:
                    isRestoreTestBatch = self._testBatchStateMap.get(coreId)
                    if isRestoreTestBatch:
                        connectionMgr = self._getCMgr(coreId)
                        ic.CTestCaseController.setTestBatch(connectionMgr, False)

            except Exception:
                print('EXCEPTION: ', traceback.format_exc())
                # ignored exception, because it occurs only on
                # very bad state, for example when user switches off
                # emulator - no need to inform him about error

            self._testBatchStateMap.clear()


    def _runTestsRecursive(self, testSpec, extensionObj, monitor,
                           filterCtrl, testFilter, isDebugMode):

        # merge base test spec and the derived one into one test spec
        mergedTestSpec = testSpec.merge()

        if testSpec.getRunFlag() != ic.E_FALSE and not mergedTestSpec.isEmptyExceptDerived():

            if monitor != None  and  monitor.isCanceled():
                raise Exception('Test execution canceled!')

            coreId = self._getConfiguredCoreID(testSpec.getCoreId())
            isTestBatchOn = self._testBatchStateMap.get(coreId)
            if isTestBatchOn is None:
                isTestBatchOn = False

            if self._isTestExecutable(mergedTestSpec, filterCtrl, testFilter, extensionObj, True):

                if self._testCaseInitConfig != None:
                    if self.connectionMgr is None:
                        debug = self._mccMgr.getCDebugFacade(coreId)
                        cmgr = self._mccMgr.getConnectionMgr(coreId)
                    else:
                        debug = ic.CDebugFacade(self.connectionMgr)
                        cmgr = self.connectionMgr

                    isTestBatchOn = ic.CTestBench.execTestCaseInitSequence(self._testCaseInitConfig,
                                                           cmgr,
                                                           debug,
                                                           self._initTargetForTestCaseTimeout,
                                                           isTestBatchOn)

                if monitor != None:
                    monitor.subTask('Executing test: ' + testSpec.getTestId() + " / " +
                                    testSpec.getFunctionUnderTest(True).getName())

                    if hasattr(monitor, "setTestInfo"):
                        monitor.setTestInfo(testCase=mergedTestSpec)

                try:
                    testCaseHostVars = self._hostVars[-1]
                    testCaseHostVars.initTestCaseVars(mergedTestSpec, None)
                    analyzerFilesToMerge = self._getFilesForCvrgMerge(mergedTestSpec,
                                                                      filterCtrl,
                                                                      extensionObj)

                    self._itest(testSpec,
                                mergedTestSpec,
                                extensionObj,
                                self._hostVars[-1],
                                analyzerFilesToMerge,
                                isTestBatchOn,
                                isDebugMode,
                                monitor)
                except Exception:
                    exMsg = traceback.format_exc()
                    result = ic.CTestResult(mergedTestSpec, exMsg)
                    self._resultContainer.putTestResult(testSpec, result)

                if monitor != None:
                    monitor.worked(1)

        numDerivedTestSpecs = testSpec.getNoOfDerivedSpecs()

        self._hostVars.append(ic.CTestHostVars(self._hostVars[-1]))

        for idx in range(0, numDerivedTestSpecs):
            self._runTestsRecursive(testSpec.getDerivedTestSpec(idx), extensionObj,
                                    monitor, filterCtrl, testFilter, isDebugMode)

        self._hostVars.pop()


    def _runGroupScripts(self,
                         rootGroup,
                         groupSection,
                         scriptFuncType,
                         envConfig,
                         monitor,
                         extensionObj):

        hostVars = ic.CTestHostVars()

        childGroups = rootGroup.getChildren(True)
        numGroups = childGroups.size()
        for idx in range(numGroups):
            childGroup = ic.CTestGroup.cast(childGroups.get(idx))
            scriptFunc = childGroup.getScriptFunction(groupSection, True)

            if scriptFunc.getName():

                monitor.subTask("Executing group script '" + scriptFunc.getName() + "()'")

                hostVars.initTestGroupVars(childGroup, envConfig)

                scriptResult = self._callCTestFunction(childGroup,
                                                       hostVars,
                                                       scriptFuncType,
                                                       scriptFunc,
                                                       extensionObj)

                groupResult = self._resultContainer.getGroupResult(childGroup)
                if groupResult is None:
                    groupResult = ic.CTestGroupResult(childGroup)
                    self._resultContainer.putTestResult(childGroup, groupResult)

                self._setScriptResult(groupResult, scriptResult)

            self._runGroupScripts(childGroup, groupSection, scriptFuncType,
                                  envConfig, monitor, extensionObj)


    def _getFilesForCvrgMerge(self, mergedTestSpec, filterCtrl, extensionObj):

        container = ic.CTestBench.getCvrgFilterCandidates(mergedTestSpec)

        trdFileList = ic.StrVector()

        analyzer = mergedTestSpec.getAnalyzer(True)
        cvrg = analyzer.getCoverage(True)

        testFilter = cvrg.getMergeFilter(True)
        numTests = container.getNoOfDerivedSpecs()

        for idx in range(numTests):
            testSpec = container.getDerivedTestSpec(idx)

            # if this method was called from method itest(), it can happen that
            # filterCtrl is None, since it is a new parameter. Check for this
            # possibility and issue a meaningful error.
            if testFilter and not filterCtrl:
                raise Exception("If coverage info in test case is merged, then filter controller\n"
                                + "must be specified when calling method itest(). See doc for\n"
                                + "method itest() for more info.")

            if self._isTestExecutable(testSpec, filterCtrl, testFilter, extensionObj, False):
                testResult = self._resultContainer.getTestResult(testSpec)
                if testResult is None:
                    # we could try to get analyzer file name from test case, but this is
                    # tricky, since analyzer file names may contain date/time/uid
                    # components, and this approach would not work in these cases.
                    # Furthermore, information in these trd files may be
                    # outdated. If users want to test one test case which merges
                    # coverage info, they can select 'Test | Keep Test Results'.
                    raise Exception("Test case has no result to use for coverage merging!" +
                                    "\ntestCaseWithMergedCoverage" + mergedTestSpec.getTestId() +
                                    "\ntestCaseWithMissingResult" + testSpec.getTestId())

                analyzerFileName = testResult.getAnalyzerFileName()
                if analyzerFileName:
                    trdFileList.append(analyzerFileName)

                    if testSpec.getAnalyzer(True).isSaveAfterTest() != ic.E_TRUE:
                        raise Exception("All files must be saved when merging coverage! "
                            + "Set option 'Save after test' in Analyzer section!"
                            + " Test case performing merge: " + mergedTestSpec.getTestId()
                            + " Test case without saved analyzer file: " + testSpec.getTestId())

        return trdFileList


    def _configureHostVars(self, dirs, envConfig):

        rootHostVars = ic.CTestHostVars()
        rootHostVars.setDirs(dirs.getWinIDEAWorkspaceDir(),
                             dirs.getIyamlDir(),
                             dirs.getReportDir())

        if envConfig != None:
            rootHostVars.setDefaultCoreId(envConfig.getConfiguredCoreID(""))
        else:
            rootHostVars.setDefaultCoreId("")

        rootHostVars.initEnvVars()
        rootHostVars.initBatchVars()

        self._hostVars = []
        self._hostVars.append(rootHostVars)


    def _isTestExecutable(self,
                          testSpec,
                          filterCtrl,
                          testFilter,
                          extensionObject,
                          isTestSpecMerged):
        """
        Returns true, if the test is executable according to the 'run'
        flag in test specification and filter settings.

        Parameters:

        testSpec: instance of CTestSpecification

        testFilter: instance of CTestFilter or None
        """
        if testSpec.getRunFlag() == ic.E_FALSE:
            return False

        if testSpec.isEmptyExceptDerived():
            return False

        # if filter is not specified, run all tests
        if testFilter is None:
            return True

        if testFilter.getFilterType() == ic.CTestFilter.SCRIPT_FILTER:
            scriptFuncParams = ic.StrVector()
            testFilter.getScriptFunctionParams(scriptFuncParams)

            scriptOut = self._callScriptFunction(testSpec,
                                                 testFilter.getScriptFunction(),
                                                 scriptFuncParams,
                                                 extensionObject,
                                                 "")
            return len(scriptOut[2]) > 0  # scriptOut[2] contains function return value
        else:
            if not filterCtrl:
                return False
            return filterCtrl.filterTestSpec(testSpec, isTestSpecMerged, testFilter)


    def countExecutableTests(self, testSpec, filterCtrl, testFilter, extensionObject):
        """
        This method returns the number of executable tests including
        the given testSpec and all its derived test
        specifications. Test specification is executable, if its 'run'
        flag is set to true, and it passes the given 'testFilter'.

        Parameters:
          testSpec: instance of ic.CTestSpecification

          testFilter: instance of ic.CTestFilter
        """

        count = 0

        if self._isTestExecutable(testSpec, filterCtrl, testFilter, extensionObject, False):
            count += 1

        numDerivedTestSpecs = testSpec.getNoOfDerivedSpecs()
        for idx in range(0, numDerivedTestSpecs):
            count += self.countExecutableTests(testSpec.getDerivedTestSpec(idx),
                                               filterCtrl,
                                               testFilter,
                                               extensionObject)

        return count


    def loadTestSpec(self, fileName, filePos=0):
        """
        Loads test bench data file.

        Parameters:

           fileName: name of the file to load

           filePos: offset in file to start loading from
        """
        testBench = ic.CTestBench.load(fileName, filePos)

        return testBench


    def getCoverageResults(self):
        """
        Deprecated - call getTestResults() and then getCoverageResults() on
        returned CTestResult. This method returns results ony for the first test.

        Returns coverage data recorded during test run. It returns a
        mapping of < functionName, CCoverageStatistic >
        """
        resultMap = ic.StrCoverageTestResultsMap()
        self.getTestResults()[0].getCoverageResults(resultMap)
        return resultMap


    def getProfilerCodeResults(self):
        """
        Deprecated - call getTestResults() and then getProfilerCodeResult() on
        returned CTestResult.

        Returns function profiler results recorded during test run. It returns a
        mapping of < functionName, CProfilerStatistic > for function profiling.
        """
        return None


    def getProfilerDataResults(self):
        """
        Deprecated - call getTestResults() and then getProfilerDataResult() on
        returned CTestResult.

        Returns data profiler results recorded during test run. It returns a
        mapping of < variableName, list of CProfilerStatistic > for data profiling.
        Each CProfilerStatistic from the list contains profiler statistic for
        one variable value.
        """
        return None


    def getTestResultsContainer(self):
        """
        Returns object containing test case and group results.
        """
        return self._resultContainer


    def getTestResults(self):
        """
        @deprecated since 9.12.266. Call getTestResultsContainer() instead,
        because it also provides group results, while this method returns
        only test case results.

        This method returns test results as a list of isys::CTestResult classes.
        The number of results depends on the number of tests run - each derived
        test adds one result item. Each call to methods runDerivedTests() or
        itest() clears previous results.

        Note: This method copies internal data to
        isystem.connect.TestResultsVector(), so it is recommended to
        keep the object instead of repeatedly calling this method.
        """
        testResultsVector = ic.TestResultsVector()
        self._resultContainer.resetTestResultIterator()
        while self._resultContainer.hasNextTestResult():
            testResultsVector.append(self._resultContainer.nextTestResult())

        return testResultsVector


    def saveTestResultsAsJUnit(self, fileName, testSuiteName):
        """
        This method saves test results in Junit format, so that it can be parsed
        by Jenkins/Hudson. This method creates file with one test suite.

        For details about the format see:
        https://stackoverflow.com/questions/4922867/junit-xml-format-specification-that-hudson-supports

        XSD:
        https://svn.jenkins-ci.org/trunk/hudson/dtkit/dtkit-format/dtkit-junit-model/src/main/resources/com/thalesgroup/dtkit/junit/model/xsd/junit-4.xsd

        Instead of class name function name is written, and test case ID is used
        as contents of 'name' attribute.

        Parameters:

        fileName - name of file to save report to
        testSuiteName - name of test suite which is used for attribute name:
                        '<testsuite name="' + testSuiteName + '" ...

        Example:
        <testsuites tests="3" errors="0" failures="0">
          <testsuite tests="3" errors="0" failures="0">
            <testcase classname="add_int" name="test-0"/>
            <testcase classname="add_int" name="test-1"
              <error type="exception"/>Invalid value!</error>
            </testcase>
            <testcase classname="max_int" name="test-2">
              <failure type="expression"/>
            </testcase>
          </testsuite>
        </testsuites>
        """

        reportStats = self.getReportStatistics()

        with open(fileName, 'w') as of:
            self.saveTestResultsAsJUnitStart(of,
                                             testSuiteName,
                                             self._resultContainer.getNoOfTestResults(),
                                             reportStats.getErrors(),
                                             reportStats.getFailures())

            self.saveTestResultsAsJUnitForTestSuite(of, testSuiteName, reportStats)

            self.saveTestResultsAsJUnitEnd(of)


    def saveTestResultsAsJUnitStart(self, of, testSuitesName, tests, errors, failures):
        """
        This method saves test results in Junit format, so that it can be parsed
        by Jenkins/Hudson. Use this method when you want to save several test sessions
        into one file. Typical usage:

            saveTestResultsAsJUnitStart(...)
            saveTestResultsAsJUnitForTestSuite(...)
            saveTestResultsAsJUnitEnd()


        Parameters:
        of - opened file stream
        testSuitesName - values for the 'name' attribute of tags 'testsuites' and
                         'testsuite'
        tests - number of all tests in test suite
        errors - number of errors
        filures - number of failures

        For details about format see method saveTestResultsAsJUnit().
        """

        of.write('<?xml version="1.0" encoding="UTF-8"?>\n')

        of.write('<testsuites name="' + testSuitesName + '" tests="' +
                 str(tests) + '" errors="' +
                 str(errors) + '" failures="' +
                 str(failures) + '">\n')


    def saveTestResultsAsJUnitEnd(self, of):
        """
        This method adds the last tag to XML file in Jenkins/Hudson format.
        See method saveTestResultsAsJUnitStart() for details.
        """
        of.write('</testsuites>\n')


    def saveTestResultsAsJUnitForTestSuite(self, of, testSuiteName, reportStats=None):
        """
        This method saves test results in Junit format, so that it can be parsed
        by Jenkins/Hudson for one test suite. Typical usage:

            saveTestResultsAsJUnitStart(...)
            saveTestResultsAsJUnitForTestSuite(...)
            saveTestResultsAsJUnitEnd()

        See method saveTestResultsAsJUnitStart() for details.
        """

        if reportStats != None:
            reportStats = self.getReportStatistics()

        of.write('  <testsuite name="' + testSuiteName + '" tests="' +
                 str(self._resultContainer.getNoOfTestResults()) + '" errors="' +
                 str(reportStats.getErrors()) + '" failures="' +
                 str(reportStats.getFailures()) + '">\n')

        self._resultContainer.resetTestResultIterator()
        while self._resultContainer.hasNextTestResult():

            tr = self._resultContainer.nextTestResult()

            of.write('    <testcase classname="' +
                     self._replaceXMLEntities(self._getJUnitClassName(tr)) +
                     '" name="' +
                     tr.getTestId() + '">\n')

            if tr.isError():
                if tr.isException():
                    of.write('      <error type="exception">\n')
                    of.write(self._replaceXMLEntities(tr.getExceptionString()))
                    of.write('      </error>\n')
                else:
                    errList = []
                    if tr.isExpressionError():
                        errList.append('expression')
                    if tr.isPreConditionError():
                        errList.append('preCondition')
                    if tr.isTargetExceptionError():
                        errList.append('targetException')
                    if tr.isCodeCoverageError():
                        errList.append('codeCoverage')
                    if tr.isProfilerCodeError():
                        errList.append('profilerCode')
                    if tr.isProfilerDataError():
                        errList.append('profilerData')
                    if tr.isScriptError():
                        errList.append('script')
                    if tr.isTestPointError():
                        errList.append('testPoint')
                    if tr.isStubError():
                        errList.append('stub')
                    if tr.isStackUsageError():
                        errList.append('stackUsage')

                    of.write('      <failure type="' + ", ".join(errList) + '"/>\n')

            of.write('    </testcase>\n')
        of.write('  </testsuite>\n')


    def _replaceXMLEntities(self, message):

        message = message.replace('&', '&amp;') # must be the first one,
                                                # otherwise '&' from other
                                                # escapes will be replaced.
        message = message.replace('<', '&lt;')
        message = message.replace('>', '&gt;')
        message = message.replace('"', '&quot;')
        message = message.replace("'", '&apos;')
        return message


    def _getJUnitClassName(self, testResult):
        testSpec = testResult.getTestSpecification()
        if testSpec:
            if testSpec.getTestScope() == ic.CTestSpecification.E_UNIT_TEST:
                # do not compose package name from parent test IDs
                # like it it done for system tests, because then the
                # same function could be shown like it is differernt
                # function (the same name in different packages)
                return testResult.getFunction()
            else:
                # since there is no meaningful classifier for system tests,
                # we add testIDs of parents as path. Thsi way users can make
                # results more structured.
                derivedTestPath = ''
                parentTestSpec = testSpec.getParentTestSpecification() # get to test spec from model
                if parentTestSpec:
                    parentTestSpec = parentTestSpec.getParentTestSpecification()
                    while parentTestSpec:
                        testId = parentTestSpec.getTestId()
                        if testId: # root test spec has empty test ID
                            if derivedTestPath:  # prepend dot if not empty
                                derivedTestPath = '.' + derivedTestPath
                            derivedTestPath = testId + derivedTestPath
                            
                        parentTestSpec = parentTestSpec.getParentTestSpecification()

                    if not derivedTestPath:
                        derivedTestPath = 'root'
                            
                return "system__test." + derivedTestPath
        else:
            return "iSYSTEM_test"

        
    def getReportStatistics(self):
        """
        Returns instance of CTestReportStatistic() from results of last run.
        """
        reportStats = ic.CTestReportStatistic()
        self._resultContainer.resetTestResultIterator()
        while self._resultContainer.hasNextTestResult():
            reportStats.analyzeResult(self._resultContainer.nextTestResult())

        return reportStats


    def reset(self):
        """
        This method resets the test subsystem in winIDEA. Use it, when
        invalid state is reported when calling the itest() method.
        """
        ic.CTestCaseController.clearAllTests(self._getPrimaryCMgr())


    def execCustomScript(self, extensionObject, extMethod, reportConfig):
        """ This method executes the given extension method. """
        if extMethod in dir(extensionObject):
            res = self._callScriptFunction(None,
                                           extMethod,
                                           # use multiline string quotes to avoid
                                           # problems because of quotes in
                                           # report config data, and raw string
                                           # because of '\' in file names
                                           ['r"""' + reportConfig.toString() + '"""'],
                                           extensionObject,
                                           ic.CScriptConfig.EXT_METHOD_TYPE)
            return res[1] # script info

        return None


    def _getPrimaryCMgr(self):
        if self.connectionMgr != None:
            return self.connectionMgr

        return self._mccMgr.getConnectionMgr("")


    def _getCMgr(self, coreId):
        if self.connectionMgr != None:
            return self.connectionMgr

        return self._mccMgr.getConnectionMgr(coreId)


    def _createTestSpecification(self, yamlTestSpec):
        """
        Parses test specification.


        Parameters:

        yamlTestSpec: test specification in YAML format. See User's
                              guide for detailed description

        Returns: instance of 'ic.CTestSpecification()' filled with
                         data from 'yamlTestSpec'
        """

        testSpec = ic.CTestSpecification.parseTestSpec(yamlTestSpec)

        return testSpec


    def _callCTestFunction(self, testSpec, hostVars, funcType, cTestFunction, extensionObj):
        """
        Calls script method as defined in 'CTestFunction' object.


        Parameters:

        cTestFunction: object of type CTestFunction

        extensionObj: object with method of the same name as returned
                                 by 'cTestFunction.getName()'.
        """

        if not cTestFunction.getName():
            return "" # OK, no function is specified

        functionName = cTestFunction.getName()
        scriptParams = ic.StrVector()

        if cTestFunction.hasPositionParams():
            cTestFunction.getPositionParams(scriptParams)

        for idx in range(0, scriptParams.size()):
            scriptParams[idx] = hostVars.replaceHostVars(scriptParams[idx])

        return self._callScriptFunction(testSpec, functionName, scriptParams,
                                        extensionObj, funcType)


    def _callScriptFunction(self, _isys_testSpec, functionName,
                            paramsStrVector, extensionObj, funcType):
        """
        Calls custom script funciton.

        IMPORTANT: Parameter name '_isys_testSpec' is defined in
        'Script.java', and it is very important to use the same string
        here, because it may be specified in parameter
        'paramsStrVector'!

        """
        if extensionObj is None:
            raise Exception("Test specification defines custom function, but" +
                            " in method itest() parameter 'extensionObj is None'. " +
                            "Custom function: '" + functionName + "'")

        params = list(paramsStrVector)
        strParams = ''
        comma = ''
        for strParam in params:
            strParams += comma
            strParams += strParam
            comma = ', '

        retVal = eval('extensionObj.' + functionName + '(' + strParams + ')')

        scriptInfo = self._getScriptInfo(extensionObj, funcType)

        if retVal is None:
            retVal = ''

        if scriptInfo is None:
            scriptInfo = ''

        return [funcType, str(scriptInfo), str(retVal)]


    def _getScriptInfo(self, extensionObj, funcType):

        retVal = None
        if funcType:
            varName = ic.CTestResult.funcType2PyVarName(funcType)
            # the trailing '\n' ends interactive code block (if statement)
            if hasattr(extensionObj, varName):
                retVal = getattr(extensionObj, varName)
                setattr(extensionObj, varName, None) # will clear the var,
                    # because the next time some other function will get
                    # called as for example initTarget() script, ant the
                    # user will easily forget to reset the var set in some
                    # function called before.

        return retVal


    def _callFunctionUnderTest(self, testSpec, testCaseCtrl, coverageCtrl,
                               stubs, extensionObj):
        """
        Runs function to be tested.

        All configuration must be done before calling this method,
        including parameters, variables and stubs. If stubs are hit,
        they are handled by this method.

        This method returns, when the execution stops for any other
        reason than stub.  It is recommended to check the status with
        'testCaseCtrl.getStatus()' after this method returns to make
        sure that the test ended successfully.


        Parameters:

        testCaseCtrl: object of type CTestCaseController

        stubs: ic.StrVector containing all stubs

        extensionObj: object with methods of the same name as
                                 returned by 'stub.getStubFunction()'
                                 for all stubs
        """

        isResumeCoverage = False
        extFuncResults = [] # will contain lists of two strings: [funcRetVal, funcInfo]

        while True:

            if coverageCtrl != None and isResumeCoverage:
                coverageCtrl.resume()

            testCaseCtrl.run()

            # wait with timeout, so that any waiting Python threads have opportunity
            # to run (GIL is in locked state during native calls)
            while not testCaseCtrl.waitUntilStopped(200):
                pass

            self._cTestCase.waitForAnalyzerToDownloadData()

            status = testCaseCtrl.getStatus()

            if  status == ic.IConnectTest.stateStub:
                extFuncResults.append(self._callStubs(testSpec, testCaseCtrl,
                                                      stubs, extensionObj))
            elif status == ic.IConnectTest.stateUnexpectedStop:

                isTestPoint, scripResults = self._execTestPoints(testSpec,
                                                                 testCaseCtrl,
                                                                 extensionObj)
                extFuncResults.append(scripResults)
                if not isTestPoint:
                    # not a stub, or test point, so exit a loop
                    break
            else:
                break  # any other state, including stateEnded

            isResumeCoverage = True

        if testCaseCtrl.getStatus() != ic.IConnectTest.stateEnded:
            raise Exception("Test didn't end normally. State = " + \
                            testCaseCtrl.testState2str(testCaseCtrl.getStatus()))

        return extFuncResults


    def _callStubs(self, testSpec, testCaseCtrl, stubs, extensionObj):
        """
        If current test status == IConnectTest.stateStub, this method
        finds the stub declaration from test specification. Then it
        sets data and calls stub methods in 'extensionObj'.


        Parameters:

        testCaseCtrl: object of type CTestCaseController

        stubs: ic.StrVector of all stubs

        extensionObj: object with methods of the same name as
                                 returned by 'stub.getStubFunction()'
                                 for all stubs
        """

        scriptParams = ic.StrVector()
        tpResult = ic.CTestPointResult()

        stub = self._cTestCase.callStubs(False,
                                         scriptParams, tpResult)

        scriptFuncName = stub.getScriptFunctionName()

        stubExtFuncResult = self._runScriptWTPResult(testSpec,
                                                     scriptFuncName,
                                                     scriptParams,
                                                     tpResult,
                                                     ic.CTestResultBase.SE_STUB,
                                                     extensionObj)

        self._cTestCase.logStatus(testCaseCtrl,
                                  stub.getLogConfig(True),
                                  ic.CTestLog.E_SECTION_AFTER,
                                  tpResult.getLogResult(False))

        return stubExtFuncResult


    def _execTestPoints(self,
                        testSpec,
                        testCaseCtrl,
                        extensionObj):

        scriptParams = ic.StrVector()
        tpResult = ic.CTestPointResult()
        extFuncResult = []

        # adds tpResult to the list of test point results in CTestCase C++ class
        testPoint = self._cTestCase.execTestPointEvalAssign(testCaseCtrl,
                                                            scriptParams,
                                                            tpResult)

        if testPoint is None:
            return False, []

        # run script only if hit count and condition are true
        if tpResult.getExecStatus() == ic.CTestPointResult.EXECUTED:
            scriptFuncName = testPoint.getScriptFunctionName()

            extFuncResult = self._runScriptWTPResult(testSpec,
                                                     scriptFuncName,
                                                     scriptParams,
                                                     tpResult,
                                                     ic.CTestResultBase.SE_TEST_POINT,
                                                     extensionObj)

        self._cTestCase.logStatus(testCaseCtrl,
                                  testPoint.getLogConfig(True),
                                  ic.CTestLog.E_SECTION_AFTER,
                                  tpResult.getLogResult(False))
        return True, extFuncResult


    def _runScriptWTPResult(self, testSpec, scriptFuncName, scriptParams, tpResult,
                            scriptType, extensionObj):

        scriptResult = []

        for idx in range(0, scriptParams.size()):
            scriptParams[idx] = self._cTestCase.replaceHostVariables(scriptParams[idx])

        if scriptFuncName:
            scriptResult = self._callScriptFunction(testSpec,
                                                    scriptFuncName,
                                                    scriptParams,
                                                    extensionObj,
                                                    scriptType)

            if scriptResult:
                # this will go to test report
                tpResult.setScriptRetVal(scriptResult[2])
                tpResult.setScriptInfoVar(scriptResult[1])

        return scriptResult


# Utility functions are following - they retrieve attribute of CTestBase and
# convert it to the expected type.
def getVector(testBase, section):
    """
      Returns string vector of the specified section.
    """
    paramsVec = ic.StrVector()
    adapter = ic.CSequenceAdapter(testBase, section, True)
    adapter.getStrVector(paramsVec, False)
    return paramsVec


def getMap(testBase, section):
    """ Returns mapping adapter for the given section. """
    mapSection = ic.StrStrMap()
    adapter = ic.CMapAdapter(testBase, section, True)
    adapter.getStrStrMap(mapSection, False)
    return mapSection


def getKeys(testBase, section):
    """ Returns StrVector of keys for the given mapping section. """
    keys = ic.StrVector()
    adapter = ic.CMapAdapter(testBase, section, True)
    adapter.getKeys(keys, False)
    return keys
