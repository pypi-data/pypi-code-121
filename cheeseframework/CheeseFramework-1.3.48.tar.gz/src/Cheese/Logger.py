#cheese

import inspect
import os
import logging

from traceback import format_exc
from datetime import datetime

from Cheese.resourceManager import ResMan
from Cheese.appSettings import Settings

class FileFilter(logging.Filter):
    def filter(self, rec):
        if (rec.levelno == logging.FILE):
            rec.msg = rec.msg.replace(Logger.HEADER, "")
            rec.msg = rec.msg.replace(Logger.OKBLUE, "")
            rec.msg = rec.msg.replace(Logger.OKCYAN, "")
            rec.msg = rec.msg.replace(Logger.OKGREEN, "")
            rec.msg = rec.msg.replace(Logger.WARNING, "")
            rec.msg = rec.msg.replace(Logger.FAIL, "")
            rec.msg = rec.msg.replace(Logger.ENDC, "")
            rec.msg = rec.msg.replace(Logger.BOLD, "")
            rec.msg = rec.msg.replace(Logger.UNDERLINE, "")
            return True
        return False

class HtmlFilter(logging.Filter):
    def filter(self, rec):
        if (not Logger.initialized): return False
        if (rec.levelno == logging.HTML_FILE):
            rec.msg = rec.msg.replace(Logger.HEADER, "<label class='header'>")
            rec.msg = rec.msg.replace(Logger.OKBLUE, "<label class='okBlue'>")
            rec.msg = rec.msg.replace(Logger.OKCYAN, "<label class='okCyan'>")
            rec.msg = rec.msg.replace(Logger.OKGREEN, "<label class='okGreen'>")
            rec.msg = rec.msg.replace(Logger.WARNING, "<label class='warning'>")
            rec.msg = rec.msg.replace(Logger.FAIL, "<label class='fail'>")
            rec.msg = rec.msg.replace(Logger.ENDC, "</label>")
            rec.msg = rec.msg.replace(Logger.BOLD, "<label class='bold'>")
            rec.msg = rec.msg.replace(Logger.UNDERLINE, "<label class='underLine'>")
            rec.msg = rec.msg.replace("\n", "<br>")
            return True
        return False

class ConsoleFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno == logging.CONSOLE

class Logger:

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    handlers = []

    initialized = False

    @staticmethod
    def initLogger():
        if (not os.path.exists(ResMan.logs())):
            os.mkdir(ResMan.logs())
        Logger.initialized = True

        htmlFormatter = logging.Formatter(fmt="<tr><td>%(asctime)s</td><td>%(message)s</td></tr>", datefmt="%Y-%m-%d %H:%M:%S")

        date = datetime.now()
        #fileHandler = logging.FileHandler(ResMan.joinPath(ResMan.logs(), f"log{date.strftime('%Y-%m-%d-%H-%M-%S')}.log"), mode="w")
        #fileHandler.setFormatter(logFormatter)
        #fileHandler.addFilter(FileFilter())
        #Logger.rootLogger.addHandler(fileHandler)
        #Logger.handlers.append(fileHandler)
        
        htmlHandler = logging.FileHandler(ResMan.joinPath(ResMan.logs(), f"log{date.strftime('%Y-%m-%d-%H-%M-%S')}.html"), mode="a")
        htmlHandler.setFormatter(htmlFormatter)
        htmlHandler.addFilter(HtmlFilter())
        Logger.rootLogger.addHandler(htmlHandler)
        Logger.handlers.append(htmlHandler)

    @staticmethod
    def set():
        Logger.__addLoggingLevel("HTML_FILE", 11)
        Logger.__addLoggingLevel("FILE", 10)
        Logger.__addLoggingLevel("CONSOLE", 9)

        logFormatter = logging.Formatter(fmt="%(asctime)s - %(message)s", datefmt="%H:%M:%S")
        Logger.rootLogger = logging.getLogger()

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        consoleHandler.addFilter(ConsoleFilter())
        Logger.rootLogger.addHandler(consoleHandler)

        Logger.rootLogger.setLevel(logging.CONSOLE)

    @staticmethod
    def close():
        for handler in Logger.handlers:
            handler.close()
    
    @staticmethod
    def info(message, allowHeader=True, silence=True):
        if (allowHeader): header = Logger.__getMethod()
        else: header = ""
        logging.file(header + message)
        message = Logger.__infoPrint(message, header)
        if (Settings.allowDebug or not silence):
            logging.console(message)
            logging.html_file(message)

    @staticmethod
    def okBlue(message, allowHeader=True, silence=True):
        if (allowHeader): header = Logger.__getMethod()
        else: header = ""
        logging.file(header + message)
        message = Logger.__okBluePrint(message, header)
        if (Settings.allowDebug or not silence):
            logging.console(message)
            logging.html_file(message)

    @staticmethod
    def okCyan(message, allowHeader=True, silence=True):
        if (allowHeader): header = Logger.__getMethod()
        else: header = ""
        logging.file(header + message)
        message = Logger.__okCyanPrint(message, header)
        if (Settings.allowDebug or not silence):
            logging.console(message)
            logging.html_file(message)

    @staticmethod
    def okGreen(message, allowHeader=True, silence=True):
        if (allowHeader): header = Logger.__getMethod()
        else: header = ""
        logging.file(header + message)
        message = Logger.__okGreenPrint(message, header)
        if (Settings.allowDebug or not silence):
            logging.console(message)
            logging.html_file(message)

    @staticmethod
    def warning(message, allowHeader=True, silence=True):
        if (allowHeader): header = Logger.__getMethod()
        else: header = ""
        logging.file(header + message)
        message = Logger.__warningPrint(message, header)
        if (Settings.allowDebug or not silence):
            logging.console(message)
            logging.html_file(message)

    @staticmethod
    def fail(message, allowHeader=True, silence=True):
        if (allowHeader): header = Logger.__getMethod()
        else: header = ""
        message = f"\n{format_exc()}\n{20*'=='}\n{message}\n{10*'='}"
        logging.file(header + message)
        message = Logger.__failPrint(message, header)
        logging.html_file(message)
        if (Settings.allowDebug or not silence):
            logging.console(message)

    @staticmethod
    def adminInfo(message, allowHeader=False, silence=False):
        if (allowHeader): header = Logger.__getMethod()
        else: header = ""
        logging.file(header + message)
        message = Logger.__warningPrint(message, header)
        logging.html_file(message)
        if (Settings.allowDebug or not silence):
            logging.console(message)

    @staticmethod
    def bold(message, allowHeader=True, silence=True):
        if (allowHeader): header = Logger.__getMethod()
        else: header = ""
        logging.file(header + message)
        message = Logger.__boldPrint(message, header)
        if (Settings.allowDebug or not silence):
            logging.console(message)
            logging.html_file(message)

    @staticmethod
    def underline(message, allowHeader=True, silence=True):
        if (allowHeader): header = Logger.__getMethod()
        else: header = ""
        logging.file(header + message)
        message = Logger.__underlinePrint(message, header)
        if (Settings.allowDebug or not silence):
            logging.console(message)
            logging.html_file(message)

    @staticmethod
    def listLogs():
        for root, dirs, files in os.walk(ResMan.logs()):
            with open(ResMan.joinPath(ResMan.admin(), "allLogs.html"), "r") as temp:
                data = temp.read()
            
            table = "<tr><th>Log name</th><th>Redirect</th><th>Status</th><th>Last logged</th><th>Size</th>"
            i = 0
            for name in reversed(sorted(files)):
                status = ""
                i += 1
                if (not name.endswith(".html")): continue
                table += f"<tr><td>{name}</td>"
                if (i == 1):
                    table += f"<td><button onclick=\"location='/admin/logs/{name}'\">Connect to active console</button></td>"
                    status = f"<td class='okGreen'>ACTIVE</td>"
                else:
                    table += f"<td><button onclick=\"location='/admin/logs/{name}'\">Show log</button></td>"
                    status = f"<td class='fail'>CLOSED</td>"
                
                with open(ResMan.joinPath(ResMan.logs(), name), "r") as log:
                    logs = log.readlines()
                    if (len(logs) > 0): 
                        for i in range(1, len(logs)):
                            if (logs[-i].startswith("<tr>")):
                                lastLogged = logs[-i].split("</td>")[0].replace("<tr><td>", "")
                    else:
                        dt = datetime.fromtimestamp(os.stat(ResMan.joinPath(ResMan.logs(), name)).st_mtime)
                        lastLogged = dt.strftime("%Y-%m-%d %H:%M:%S")
                        if (i == 1):
                            status = f"<td class='okGreen'>ACTIVE/EMPTY</td>"
                        else:
                            status = f"<td class='warning'>EMPTY</td>"

                table += status
                table += f"<td>{lastLogged}</td>"
                table += f"<td>{ResMan.convertBytes(os.path.getsize(ResMan.joinPath(ResMan.logs(), name)))}</td>"
                if (i != 1):
                    table += f"<td><button onclick=\"deleteFile('{name}')\">Remove log</button></td></tr>"

            data = data.replace("TABLE", table)
            return (bytes(data, "utf-8"), 200)

    @staticmethod
    def serveLogs(server):
        path = server.path
        if (path == "/admin/logs" or path == "/admin/logs/"):
            logging.file(f"listing log files: {server.client_address[0]}")
            return Logger.listLogs()

        log = ResMan.joinPath(ResMan.root(), path.replace("/admin", ""))
        logging.file(f"Serving log file: {server.client_address[0]} \"{server.path}\"")
        
        if (not os.path.exists(f"{log}")):
            with open(f"{ResMan.error()}/error404.html", "rb") as f:
                return (f.read(), 404)

        with open(ResMan.joinPath(ResMan.admin(), "activeLog.html"), "r") as temp:
            logName = ResMan.getFileName(log).replace(".html", "")
            for root, dirs, files in os.walk(ResMan.logs()):
                if (sorted(files)[-1] == logName + ".html"):
                    data = temp.read()
                else:
                    with open(f"{log}", "r") as f:
                        data = temp.read()
                        data = data.replace('class="logTable">', 'class="logTable">' + f.read())
                        data = data.replace("Cheese log - ", "Cheese log - " + 
                            logName + " - <label class='fail'>CLOSED</label>")
                        data = data.replace("//dontRunScript", "dontRunScript")
        return (bytes(data, "utf-8"), 200)
                

    #PRIVATE METHODS

    @staticmethod
    def __addLoggingLevel(levelName, levelNum, methodName=None):
        if not methodName:
            methodName = levelName.lower()

        if hasattr(logging, levelName):
            raise AttributeError('{} already defined in logging module'.format(levelName))
        if hasattr(logging, methodName):
            raise AttributeError('{} already defined in logging module'.format(methodName))
        if hasattr(logging.getLoggerClass(), methodName):
            raise AttributeError('{} already defined in logger class'.format(methodName))

        def logForLevel(self, message, *args, **kwargs):
            if self.isEnabledFor(levelNum):
                self._log(levelNum, message, args, **kwargs)
        def logToRoot(message, *args, **kwargs):
            logging.log(levelNum, message, *args, **kwargs)

        logging.addLevelName(levelNum, levelName)
        setattr(logging, levelName, levelNum)
        setattr(logging.getLoggerClass(), methodName, logForLevel)
        setattr(logging, methodName, logToRoot)

    @staticmethod
    def __getMethod():
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        classFile = ResMan.getFileName(calframe[3].filename)
        function = calframe[3].function
        return f"{Logger.BOLD}{classFile}->{function}: {Logger.ENDC}"

    @staticmethod
    def __infoPrint(message, header):
        return header + message

    @staticmethod
    def __okBluePrint(message, header):
        return header + Logger.OKBLUE + message + Logger.ENDC

    @staticmethod
    def __okCyanPrint(message, header):
        return header + Logger.OKCYAN + message + Logger.ENDC

    @staticmethod
    def __okGreenPrint(message, header):
        return header + Logger.OKGREEN + message + Logger.ENDC

    @staticmethod
    def __warningPrint(message, header):
        return header + Logger.WARNING + message + Logger.ENDC

    @staticmethod
    def __failPrint(message, header):
        return header + Logger.FAIL + message + Logger.ENDC

    @staticmethod
    def __boldPrint(message, header):
        return header + Logger.BOLD + message + Logger.ENDC

    @staticmethod
    def __underlinePrint(message, header):
        return header + Logger.UNDERLINE + message + Logger.ENDC

Logger.set()