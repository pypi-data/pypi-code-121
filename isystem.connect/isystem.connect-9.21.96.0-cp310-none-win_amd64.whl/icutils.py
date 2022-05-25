"""
This module is deprecated. Instead of using ICFactory class,
connect to winIDEA using class ConnectionMgr(). This way you have more
options to connect to the desired winIDEA instance.

Example:

import isystem.connect as ic

cmgr = ic.ConnectionMgr()
cmgr.connectMRU('')

dbg = ic.CDebugFacade(cmgr)


Old example:

from isystem import icutils

icFactory = icutils.getFactory()

dbg = icFactory.getDebugFacade()

"""

import isystem.connect

# For versioning see also http://www.python.org/dev/peps/pep-0008/,
# section 'Version bookkeeping'.
# Contains version info about this product.
__version__ = isystem.connect.getModuleVersion()

g_defaultFactory = None

# When called from winIDEA, workspaceFileName should be None,
# and winIDEAConnect() should be called on returned object.
def getFactory(workspaceFileName=''):
    """
    This function is preferred method for instantiating ICFactory
    class. It always returns the same instance of ICFactory class
    connected to winIDEA.

    If more than one connection is required (for example in case of
    multi-core targets, other connections can be done by directly
    instantiating the ICFactory class.

    Returns: ICFactory connected to winIDEA instance

    See also: ICFactory.__init__() for detailed description of parameter.

    Example:
    --------

    from isystem import icutils

    icFactory = icutils.getFactory()

    dbg = icFactory.getDebugFacade()

    dbg.download()
    dbg.setBP('main')
    dbg.run()
    """
    global g_defaultFactory
    if g_defaultFactory is None:
        g_defaultFactory = ICFactory(workspaceFileName)

    return g_defaultFactory


class ICFactory:
    """
    This class is deprecated. Instead of using it, connect to winIDEA
    using class ConnectionMgr(). This way you have more options to
    connect to the desired winIDEA instance.

    Example:

    import isystem.connect as ic

    cmgr = ic.ConnectionMgr()
    cmgr.connectMRU('')

    dbg = ic.CDebugFacade(cmgr)


    Old example using this class:

    from isystem import icutils

    icFactory = icutils.ICFactory('')

    debug = icFactory.getDebugFacade()
    debug.download()
    """
    _connectionMgr = None

    _debugCtrl = None
    _dataCtrl = None
    _projectCtrl = None
    _terminalDocCtrl = None
    _hilCtrl = None
    _ideCtrl = None
    _workspaceCtrl = None
    _coverageCtrl = None
    _profilerCtrl = None
    _testCaseCtrl = None

    def __init__(self, workspaceFileName=''):
        """
        Instantiates this class and connects to winIDEA, depending on
        the values of parameter:

            If 'workspaceFileName is None', no connection is
            established. You should call 'connect()' before any other
            operation.

            If workspaceFileName == '' (empty string),
            connection is made to winIDEA with the most recently used
            workspace.

            If 'workspaceFileName == <workspaceFileName>',
            connection is made to winIDEA with the given workspace.
        """
        if workspaceFileName != None:
            self.connect(workspaceFileName)


    def connect(self, workspaceFileName=''):
        """
        Connects to winIDEA and loads the given workspace. If no
        workspace file is specified, the most recently used workspace
        is opened.
        """
        if self._connectionMgr is None:
            self._connectionMgr = isystem.connect.ConnectionMgr()
            self._connectionMgr.connectMRU(workspaceFileName)
        else:
            raise Exception("This instance of ICFactory is already connected!" +
                            " Create another instance to make another connection!")

    def connectWithId(self, winIdeaId):
        """
        Connects to winIDEA, which was started with the specified winIdeaId (command line
        option /id:<idString>). If such instance of winIDEA is not found, an
        exception is raised.
        """
        self._connectionMgr = isystem.connect.ConnectionMgr()
        connectionConfig = isystem.connect.CConnectionConfig()
        connectionConfig.instanceId(winIdeaId)
        port = 0
        port = self._connectionMgr.findExistingInstance('', connectionConfig)
        if port < 0:
            raise Exception("winIDEA with id == '" + str(winIdeaId) + "' not found!")
        self._connectionMgr.connect('', port)


    def getDebugFacade(self):
        """ Returns instance of CDebugFacade. """
        if self._debugCtrl is None:
            self._debugCtrl = isystem.connect.CDebugFacade(self._connectionMgr)

        return self._debugCtrl


    def getDataCtrl(self):
        """ Returns instance of CDataController. """
        if self._dataCtrl is None:
            self._dataCtrl = isystem.connect.CDataController(self._connectionMgr)

        return self._dataCtrl


    def getProjectCtrl(self):
        """ Returns instance of CProjectController. """
        if self._projectCtrl is None:
            self._projectCtrl = isystem.connect.CProjectController(self._connectionMgr)

        return self._projectCtrl


    def getDocumentCtrl(self, fileName, openMode):
        """ Returns instance of CDocumentController.

            Parameters:
              isNew    - set it to true, if new document should be opened
              fileName - name of the new document
        """
        _documentCtrl = isystem.connect.CDocumentController(self._connectionMgr, fileName, openMode)
        return _documentCtrl


    def getAnalyzerDocCtrl(self, docType, fileName, openMode):
        """ Returns instance of CAnalyzerController.

            Parameters:
              isNew    - set it to true, if new document should be opened
              fileName - name of the new document
        """
        _analyzerDocCtrl = isystem.connect.CAnalyzerDocController(self._connectionMgr,
                                                                  docType, fileName, openMode)
        return _analyzerDocCtrl


    def getTerminalDocCtrl(self):
        """ Returns instance of CTerminalController."""
        if self._terminalDocCtrl is None:
            self._terminalDocCtrl = isystem.connect.CTerminalDocController(self._connectionMgr)

        return self._terminalDocCtrl


    def getHILCtrl(self):
        """ Returns instance of CHILController."""
        if self._hilCtrl is None:
            self._hilCtrl = isystem.connect.CHILController(self._connectionMgr)
        return self._hilCtrl


    def getIdeCtrl(self):
        """ Returns instance of CIDEController."""
        if self._ideCtrl is None:
            self._ideCtrl = isystem.connect.CIDEController(self._connectionMgr)
        return self._ideCtrl


    def getWorkspaceCtrl(self):
        """ Returns instance of CWorkspaceController."""
        if self._workspaceCtrl is None:
            self._workspaceCtrl = isystem.connect.CWorkspaceController(self._connectionMgr)

        return self._workspaceCtrl


    def getProfilerCtrl(self):
        """ Returns instance of CProfilerController."""
        if self._profilerCtrl is None:
            self._profilerCtrl = isystem.connect.CProfilerController(self._connectionMgr)
        return self._profilerCtrl


    def getTestCaseCtrl(self, functionName, retValName):
        """
        Returns instance of CTestCaseController. It is caller's responsibility to
        call clean() and destroy() on returned object when it is no longer needed.
        Example:

            icFactory = isystem.icutils.getFactory()
            testCtrl = icFactory.getTestCaseCtrl("funcTestInt2", "retVal")
            testCtrl.createParameter(0, "a")
            testCtrl.createParameter(1, "b")
            testCtrl.createParameter(2, "c")
            testCtrl.init()
            testCtrl.modify("a", "11")
            testCtrl.modify("b", "21")
            testCtrl.modify("c", "31")

            testCtrl.run()
            testCtrl.waitUntilStopped()

            result = testCtrl.s2i64(testCtrl.evaluate("retVal == 64"))
            if result == 1:
                print "OK"
            else:
                print "Error: result = ", result

            # It is very important that we destroy the test case after usage!
            testCtrl.clean()
            testCtrl.destroy()

        """
        self._testCaseCtrl = isystem.connect.CTestCaseController(self._connectionMgr,
                                                                 functionName,
                                                                 retValName)
        return self._testCaseCtrl


    def getCoverageCtrl(self, fileName, openMode):
        """ Returns instance of CoverageController.

            Parameters:
              fileName - name of the new document
              openMode - 'r' opens existing file, 'w' opens
                         existing file and deletes contents or creates new file,
                         'a' opens existing file and keeps contents or creates
                         new file.
        """
        _coverageCtrl = isystem.connect.CCoverageController2(self._connectionMgr,
                                                             fileName,
                                                             openMode)
        return _coverageCtrl


    def getConnectionMgr(self):
        """
        Returns connection manager. Use this method, when you need the
        connection manager to instantiate 'isystem.connect' classes
        directly.
        """
        return self._connectionMgr
