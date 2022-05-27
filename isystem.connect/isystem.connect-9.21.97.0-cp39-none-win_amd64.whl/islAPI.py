import isystem.connect as ic
import isystem as isys
import logging
import os
import sys


class RetCode:
    SUCCESS = 1
    FAILURE = 0
    FAILURE_1 = -1
    UP_TO_DATE = 1
    NOT_UP_TO_DATE = 0
    CP_SUCCESS = 0
    CP_FAILURE = -1
    YES = 1
    NO = 0
    CANCEL_CLOSE = 0


class ExceptPrint:
    YES = True
    NO = False


class LogLevel:
    CRITICAL = 5
    ERROR = 4
    WARNING = 3
    INFO = 2
    DEBUG = 1
    NOTSET = 0

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

class IslLogger():
    def __init__(self,
                 fileLog='',
                 consoleLog=1,
                 appendToFile=False,
                 logLevel=LogLevel.INFO,
                 newLineFormat=False,
                 exceptionTB=False):
        try:
            self.consoleHandler = None
            self.fileHandler = None
            self.nullHandler = None
            
            self.consoleLog = False
            self.fileLog = ''
            
            self.exceptionTB = False
            self.newLineFormat = False
            
            self.log = logging.getLogger()
            
            self.setupLog(fileLog,
                          consoleLog,
                          appendToFile,
                          newLineFormat)
            
            self.setupLogLevel(logLevel)
        except Exception as ex:
            print(str(ex))
        
        return
    
    
    def __setupNullLog(self):
        try:
            retCode = RetCode.SUCCESS
            
            self.nullHandler = NullHandler()
            self.log.addHandler(self.nullHandler)
        except Exception as ex:
            self.nullHandler = None
            retCode = RetCode.FAILURE
        finally:
            return retCode
    
    
    def __setupConsoleLog(self, consoleLog):
        try:
            retCode = RetCode.SUCCESS
            if self.consoleHandler is not None:
                self.log.removeHandler(self.consoleHandler)
                self.consoleHandler = None
            else:
                pass
            
            if consoleLog:
                self.consoleHandler = logging.StreamHandler()
                self.log.addHandler(self.consoleHandler)
                self.consoleLog = True
            else:
                self.consoleLog = False
        except Exception as ex:
            self.consoleLog = False
            retCode = RetCode.FAILURE
        finally:
            return retCode
    
    
    def __setupFileLog(self, fileLog):
        try:
            retCode = RetCode.SUCCESS
            
            if self.fileHandler is not None:
                self.log.removeHandler(self.fileHandler)
                self.fileHandler = None
            else:
                pass
            
            if fileLog is not '':
                if os.path.exists(os.path.dirname(fileLog)):
                    self.fileHandler = logging.FileHandler(fileLog, self.appendToFile)
                    self.log.addHandler(self.fileHandler)
                    self.fileLog = fileLog
                else:
                    retCode = RetCode.FAILURE
            else:
                self.fileLog = ''
        except Exception as ex:
            self.fileLog = ''
            print(str(ex))
            retCode = RetCode.FAILURE
        finally:
            return retCode
    
    
    def setupLogLevel(self, logLevel):
        try:
            retCode = RetCode.SUCCESS
            
            log = {
                LogLevel.CRITICAL: logging.CRITICAL,
                LogLevel.ERROR: logging.ERROR,
                LogLevel.WARNING: logging.WARNING,
                LogLevel.INFO: logging.INFO,
                LogLevel.DEBUG: logging.DEBUG,
                LogLevel.NOTSET: logging.NOTSET,
                }.get(logLevel, logging.INFO)
            
            self.log.setLevel(log)
            self.logLevel = logLevel
        except Exception as ex:
            retCode = RetCode.FAILURE
        finally:
            return retCode
    
    
    def setupLog(self,
                 fileLog='',
                 consoleLog=1,
                 appendToFile=False,
                 newLineFormat=False):
        retCode = RetCode.SUCCESS
        
        self.newLineFormat = newLineFormat
        
        if consoleLog is 0:
            consoleLog = False
        else:
            consoleLog = True
        if consoleLog is not self.consoleLog:
            retCode = self.__setupConsoleLog(consoleLog)
        else:
            pass
        
        if appendToFile:
            self.appendToFile = 'a'
        else:
            self.appendToFile = 'w'
        
        if fileLog is not self.fileLog:
            retCode = self.__setupFileLog(fileLog)
        else:
            pass
        
        if self.nullHandler is None:
            retCode = self.__setupNullLog()
        else:
            pass
        
        return retCode
    
    
    def printCritical(self, msg):
        self.log.critical(msg)
        
        return
    
    def printError(self, msg):
        self.log.error(msg)
        
        return
    
    def printWarning(self, msg):
        self.log.warning(msg)
        
        return
    
    def printInfo(self, msg):
        self.log.info(msg)
        
        return
    
    def printDebug(self, msg):
        self.log.debug(msg)
        
        return
    
    def printException(self, msg):
        if self.exceptionTB:
            self.log.exception('')
        else:
            pass
        
        if msg is not '':
            self.log.info(msg)
        else:
            pass
        
        return


class IWrapper:
    def __init__(self, workspacePath=None):
        try:
            self.connectionMgr = ic.ConnectionMgr()
            
            if workspacePath is None:
                self.connectionMgr.connectMRU('')
            else:
                self.connectionMgr.connectMRU(workspacePath)
            
            self.islWrapperScript = ic.CISLScript(self.connectionMgr)
            self.islWrapperScript.service(
                    ic.SISL_IN.fInit,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log = IslLogger()
        except Exception as ex:
            print(str(ex))
        
        return
    
    def __del__(self):
        self.islWrapperScript.service(
                ic.SISL_IN.fDone,
                '',
                '',
                '',
                '',
                0,
                0,
                0,
                0,
                0,
                0)
    
    def getConnectionMgr(self):
        return self.connectionMgr
    
    def setLogger(self, logLevel=LogLevel.INFO, exceptionTB=False):
        try:
            retCode = self.log.setupLogLevel(logLevel)
            self.log.exceptionTB = exceptionTB
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIAppendOutput(self, strFileName, bOutput):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIAppendOutput,
                    strFileName, 
                    '', 
                    '',
                    '',
                    bOutput,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.setupLog(
                    fileLog = '',
                    consoleLog = bOutput)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIBeep(self):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIBeep,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIBeginTrace(self):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIBeginTrace,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIClearBreakpoint(self, iType, iHandle):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIClearBreakpoint,
                    '',
                    '',
                    '',
                    '',
                    iType,
                    iHandle,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIClearBreakpoints(self):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIClearBreakpoints,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIClearDisplay(self):
        try:
            import subprocess
            subprocess.call('cls.exe', shell=True)
            
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIClearDisplay,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APICompareFiles(self, pszFile1, pszFile2, bDumpDifLines):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPICompareFiles,
                    pszFile1,
                    pszFile2,
                    '',
                    '',
                    bDumpDifLines,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APICopyMemory(self, iFromMemArea, iFromAddress, iSize, iToMemArea, iToAddress):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPICopyMemory,
                    '',
                    '',
                    '',
                    '',
                    iFromMemArea,
                    iFromAddress,
                    iSize,
                    iToMemArea,
                    iToAddress,
                    0)
            
            if retCode is True:
                self.log.printInfo(self.islWrapperScript.getLastOutputText())
            else:
                pass
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APICreateProcess(self, strApplicationName, strCmdLine, bSync):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPICreateProcess,
                    strApplicationName,
                    strCmdLine,
                    '',
                    '',
                    bSync,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.CP_FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIDownload(self):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIDownload,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIDownloadFile(self, iFileIndex):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIDownloadFile,
                    '',
                    '',
                    '',
                    '',
                    iFileIndex,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIDownloadFile1(self, strFileName, nReserved):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIDownloadFile1,
                    strFileName,
                    '',
                    '',
                    '',
                    nReserved,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIEvaluate(self, strExpression):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIEvaluate,
                    strExpression,
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIEvaluate1(self, iAccessMethod, strExpression):
        try:
            retValue = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIEvaluate1,
                    strExpression,
                    '',
                    '',
                    '',
                    iAccessMethod,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retValue = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retValue
    
    
    def APIEvaluate2(self, nAccessMode, strExpression):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIEvaluate2,
                    strExpression,
                    '',
                    '',
                    '',
                    nAccessMode,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            if retCode is 0:
                self.log.printInfo(self.islWrapperScript.getLastOutputText())
            else:
                pass
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIExit(self, iExitCode):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIExit,
                    '',
                    '',
                    '',
                    '',
                    iExitCode,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIFillMemory(self, iAccessMethod, iMemArea, iAddress, iValue, iSize):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIFillMemory,
                    '',
                    '',
                    '',
                    '',
                    iAccessMethod,
                    iMemArea,
                    iAddress,
                    iValue,
                    iSize,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIFLASHProgramFile(self, strFileName):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIFLASHProgramFile,
                    strFileName,
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIFLASHProgramFile1(self):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIFLASHProgramFile1,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIGoto(self, iAddress):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIGoto,
                    '',
                    '',
                    '',
                    '',
                    iAddress,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIGoto1(self, strAddress):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIGoto1,
                    strAddress,
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIGotoLC(self, iLine, iColumn):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIGotoLC,
                    '',
                    '',
                    '',
                    '',
                    iLine,
                    iColumn,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIInputNumber(self, pszMessage):
        try:
            if sys.version_info.major < 3:
                import Tkinter, tkSimpleDialog
                
                parent = Tkinter.Tk()
                parent.withdraw()
                retValue = tkSimpleDialog.askinteger(pszMessage, "", initialvalue=0)
            else:
                import tkinter
                from tkinter import simpledialog
                
                parent = tkinter.Tk()
                parent.withdraw()
                retValue = simpledialog.askinteger(pszMessage, "", initialvalue=0)
            
            if retValue is None:
                retValue = RetCode.CANCEL_CLOSE
            else:
                pass
        except Exception as ex:
            retValue = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retValue
    
    
    def APILoadProject(self, strFileName):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPILoadProject,
                    strFileName,
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APILoadProject1(self, strFileName, bSaveOld):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPILoadProject1,
                    strFileName,
                    '',
                    '',
                    '',
                    bSaveOld,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIMessageBox(self, strMessage):
        try:
            if sys.version_info.major < 3:
                import Tkinter, tkMessageBox
                
                parent = Tkinter.Tk()
                parent.withdraw()
                tkMessageBox.showwarning("winIDEA", strMessage)
            else:
                import tkinter
                from tkinter import messagebox
                
                parent = tkinter.Tk()
                parent.withdraw()
                messagebox.showwarning("winIDEA", strMessage)
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIMessageBoxYesNo(self, strMessage):
        try:
            if sys.version_info.major < 3:
                import Tkinter, tkMessageBox
                
                parent = Tkinter.Tk()
                parent.withdraw()
                if tkMessageBox.askyesno("winIDEA", strMessage) is True:
                    retCode = RetCode.YES
                else:
                    retCode = RetCode.NO
            else:
                import tkinter
                from tkinter import messagebox
                
                parent = tkinter.Tk()
                parent.withdraw()
                if messagebox.askyesno("winIDEA", strMessage) is True:
                    retCode = RetCode.YES
                else:
                    retCode = RetCode.NO
        except Exception as ex:
            self.log.printException('')
            retCode = RetCode.NO
        finally:
            return retCode
    
    
    def APIModify(self, strLValue, strExpression):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIModify,
                    strLValue,
                    strExpression,
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIModify1(self, strLValue, nValue):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIModify1,
                    strLValue,
                    '',
                    '',
                    '',
                    nValue,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
            retCode = RetCode.FAILURE
        finally:
            return retCode
    
    
    def APIOpenMemoryDumpFile(self, strFileName, iForWrite):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIOpenMemoryDumpFile,
                    strFileName,
                    '',
                    '',
                    '',
                    iForWrite,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIPassParameter(self, strClass, strTitle, iParameter):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIPassParameter,
                    strClass,
                    strTitle,
                    '',
                    '',
                    iParameter,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIPrintB(self, iValue, iNumBits, iNumBlanks):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIPrintB,
                    '',
                    '',
                    '',
                    '',
                    iValue,
                    iNumBits,
                    iNumBlanks,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIPrintF1(self, strText, iV0):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIPrintF1,
                    strText,
                    '',
                    '',
                    '',
                    iV0,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIPrintF1LC(self, iLine, iColumn, strText, iV0):
        try:
            self.islWrapperScript.service(
                ic.SISL_IN.fAPIPrintF1LC,
                strText,
                '',
                '',
                '',
                iLine,
                iColumn,
                iV0,
                0,
                0,
                0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIPrintF2(self, strText, iV1, iV2):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIPrintF2,
                    strText,
                    '',
                    '',
                    '',
                    iV1,
                    iV2,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIPrintF3(self, strText, iV1, iV2, iV3):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIPrintF3,
                    strText,
                    '',
                    '',
                    '',
                    iV1,
                    iV2,
                    iV3,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIPrintInteger(self, iValue):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIPrintInteger,
                    '',
                    '',
                    '',
                    '',
                    iValue,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIPrintIntegerLC(self, iLine, iColumn, iValue):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIPrintIntegerLC,
                    '',
                    '',
                    '',
                    '',
                    iLine,
                    iColumn,
                    iValue,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIPrintString(self, strText):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPIPrintString,
                    strText,
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIPrintStringLC(self, iLine, iColumn, strText):
        try:
            self.islWrapperScript.service(
                ic.SISL_IN.fAPIPrintStringLC,
                strText,
                '',
                '',
                '',
                iLine,
                iColumn,
                0,
                0,
                0,
                0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIProjectImport(self, strImportFileName, iReserved):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIProjectImport,
                    strImportFileName,
                    '',
                    '',
                    '',
                    iReserved,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIProjectMake(self, iLinkMakeBuild):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIProjectMake,
                    '',
                    '',
                    '',
                    '',
                    iLinkMakeBuild,
                    0,
                    0,
                    0,
                    0,
                    0)
        except:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIProjectIsUpToDate(self, iReserved):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIProjectIsUpToDate,
                    '',
                    '',
                    '',
                    '',
                    iReserved,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.NOT_UP_TO_DATE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIProjectSetTarget(self, strTargetName):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIProjectSetTarget,
                    strTargetName,
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIReadInt(self, nAccessMode, nMemArea, nAddress, nSize, nBigEndian):
        try:
            retValue = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIReadInt,
                    '',
                    '',
                    '',
                    '',
                    nAccessMode,
                    nMemArea,
                    nAddress,
                    nSize,
                    nBigEndian,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retValue = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retValue
    
    
    def APIReadMemory(self, iMemArea, iAddress, iSize):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIReadMemory,
                    '',
                    '',
                    '',
                    '',
                    iMemArea,
                    iAddress,
                    iSize,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIReadMemory1(self, iAccessMethod, iMemArea, iAddress, iSize):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIReadMemory1,
                    '',
                    '',
                    '',
                    '',
                    iAccessMethod,
                    iMemArea,
                    iAddress,
                    iSize,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIReadMemory2(self, iAccessMethod, strLocation, iSize):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIReadMemory2,
                    strLocation,
                    '',
                    '',
                    '',
                    iAccessMethod,
                    iSize,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIReadMemoryDump(self, iAccessMode, iMemArea, iAddress, iSize, iReserved):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIReadMemoryDump,
                    '',
                    '',
                    '',
                    '',
                    iAccessMode,
                    iMemArea,
                    iAddress,
                    iSize,
                    iReserved,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIReapplyBreakpoints(self):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIReapplyBreakpoints,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIReset(self, bAndRun):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIReset,
                    '',
                    '',
                    '',
                    '',
                    bAndRun,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIRun(self):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIRun,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APISaveAccessCoverage(self, strFileName, nFlags):
        try:
            retCode = RetCode.FAILURE
            
            self.log.printDebug('APISaveAccessCoverage(): function not supported')
            
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APISaveExecutionCoverage(self, strFileName, nFlags):
        try:
            retCode = RetCode.FAILURE
            
            self.log.printDebug('APISaveExecutionCoverage(): function not supported')
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APISaveProfiler(self, strFileName, nFlags):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPISaveProfiler,
                    strFileName,
                    '',
                    '',
                    '',
                    nFlags,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APISaveProject(self, strFileName):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPISaveProject,
                    strFileName,
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APISaveTrace(self, strFileName, nFlags):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPISaveTrace,
                    strFileName,
                    '',
                    '',
                    '',
                    nFlags,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APISetBreakpoint(self, iType, strBP):
        try:
            retValue = self.islWrapperScript.service(
                    ic.SISL_IN.fAPISetBreakpoint,
                    strBP,
                    '',
                    '',
                    '',
                    iType,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retValue = RetCode.FAILURE_1
            self.log.printException('')
        finally:
            return retValue
    
    
    def APISetOutput(self, strFileName, bOutput):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPISetOutput,
                    strFileName,
                    '',
                    '',
                    '',
                    bOutput,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.setupLog(
                fileLog = '',
                consoleLog = bOutput)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APISetOutput1(self, strFileName, bOutput, bNoDefaultCRLF):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPISetOutput1,
                    strFileName,
                    '',
                    '',
                    '',
                    bOutput,
                    bNoDefaultCRLF,
                    0,
                    0,
                    0,
                    0)
            
            self.log.setupLog(
                fileLog = '',
                consoleLog = bOutput)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APISetRegisterDump(self, iDump):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPISetRegisterDump,
                    '',
                    '',
                    '',
                    '',
                    iDump,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APISleep(self, nMiliseconds):
        try:
            self.islWrapperScript.service(
                    ic.SISL_IN.fAPISleep,
                    '',
                    '',
                    '',
                    '',
                    nMiliseconds,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            self.log.printException('')
        finally:
            return
    
    
    def APIStepInto(self, bHighLevel, iNumSteps):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIStepInto,
                    '',
                    '',
                    '',
                    '',
                    bHighLevel,
                    iNumSteps,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIStepOver(self, iHighLevel, iNumSteps):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIStepOver,
                    '',
                    '',
                    '',
                    '',
                    iHighLevel,
                    iNumSteps,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIStop(self):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIStop,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APITerminalConnect(self, nOn):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPITerminalConnect,
                    '',
                    '',
                    '',
                    '',
                    nOn,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIVerifyDownload(self):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIVerifyDownload,
                    '',
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIWaitStatus(self, nStatus):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIWaitStatus,
                    '',
                    '',
                    '',
                    '',
                    nStatus,
                    0,
                    0,
                    0,
                    0,
                    0)
        
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIWaitStatus1(self, nStatus, iTimeout):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIWaitStatus1,
                    '',
                    '',
                    '',
                    '',
                    nStatus,
                    iTimeout,
                    0,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIWriteInt(self, nAccessMode, nMemArea, nAddress, nSize, nBigEndian, nValue):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIWriteInt,
                    '',
                    '',
                    '',
                    '',
                    nAccessMode,
                    nMemArea,
                    nAddress,
                    nSize,
                    nBigEndian,
                    nValue)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIWriteMemory(self, iMemArea, iAddress, iValue, iSize):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIWriteMemory,
                    '',
                    '',
                    '',
                    '',
                    iMemArea,
                    iAddress,
                    iValue,
                    iSize,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIWriteMemory1(self, iAccessMethod, iMemArea, iAddress, iValue, iSize):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIWriteMemory1,
                    '',
                    '',
                    '',
                    '',
                    iAccessMethod,
                    iMemArea,
                    iAddress,
                    iValue,
                    iSize,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIWriteMemory2(self, iAccessMethod, strLocation, iValue, iSize):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIWriteMemory2,
                    strLocation,
                    '',
                    '',
                    '',
                    iAccessMethod,
                    iValue,
                    iSize,
                    0,
                    0,
                    0)
            
            self.log.printInfo(self.islWrapperScript.getLastOutputText())
        except Exception as ex:
            self.log.printException('')
            retCode = RetCode.FAILURE
        finally:
            return retCode
    
    
    def APIWriteMemoryDump(self, iAccessMode, iMemArea, iAddress, iSize, iReserved):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIWriteMemoryDump,
                    '',
                    '',
                    '',
                    '',
                    iAccessMode,
                    iMemArea,
                    iAddress,
                    iSize,
                    iReserved,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def APIWriteTrace(self, strFileName, nFrom, nTo):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPIWriteTrace,
                    strFileName,
                    '',
                    '',
                    '',
                    nFrom,
                    nTo,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTSetTraceOperation(self, nOperation):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_SetTraceOperation,
                    '',
                    '',
                    '',
                    '',
                    nOperation,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTSetTraceTrigger(self, pszTrigger):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_SetTraceTrigger,
                    pszTrigger,
                    '',
                    '',
                    '',
                    0,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTWriteID(self, nID, pszDate, pszRev, nVer, pszSpec):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_WriteID,
                    pszDate,
                    pszRev,
                    pszSpec,
                    '',
                    nID,
                    nVer,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTSetMapping(self, nMemArea, dwAddress, dwStop, nType):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_SetMapping,
                    '',
                    '',
                    '',
                    '',
                    nMemArea,
                    dwAddress,
                    dwStop,
                    nType,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTSetClock(self, bInternal, dwFreq):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_SetClock,
                    '',
                    '',
                    '',
                    '',
                    bInternal,
                    dwFreq,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTShootPattern(self, pszPattern, bEnable):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_ShootPattern,
                    pszPattern,
                    '',
                    '',
                    '',
                    bEnable,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTSetAccessBP(self, nBPArea, pszBP):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_SetAccessBP,
                    pszBP,
                    '',
                    '',
                    '',
                    nBPArea,
                    0,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTClearAccessBP(self, nBPArea, nBP):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_ClearAccessBP,
                    '',
                    '',
                    '',
                    '',
                    nBPArea,
                    nBP,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTSetAccessBP1(self, nBPArea, pszBP, nRW):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_SetAccessBP1,
                    pszBP,
                    '',
                    '',
                    '',
                    nBPArea,
                    nRW,
                    0,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTSetParameter(self, nParameter, nVal1, nVal2):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_SetParameter,
                    '',
                    '',
                    '',
                    '',
                    nParameter,
                    nVal1,
                    nVal2,
                    0,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode
    
    
    def HASYSTWriteID2(self, nID, dwSerialNumber, pszRev, nVer, pszSpec, byDomain):
        try:
            retCode = self.islWrapperScript.service(
                    ic.SISL_IN.fAPI_HASYST_WriteID2,
                    pszRev,
                    pszSpec,
                    '',
                    '',
                    nID,
                    dwSerialNumber,
                    nVer,
                    byDomain,
                    0,
                    0)
        except Exception as ex:
            retCode = RetCode.FAILURE
            self.log.printException('')
        finally:
            return retCode