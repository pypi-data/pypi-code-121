#cheese

import os
import json
import time
import sys
import subprocess
import base64

from Cheese.cheeseController import CheeseController
from Cheese.variables import Variables
from Cheese.Logger import Logger
from Cheese.resourceManager import ResMan
from Cheese.appSettings import Settings
from Cheese.ErrorCodes import Error
from Cheese.metadata import Metadata

class AdminManager:

    @staticmethod
    def controller(server):
        if (not AdminManager.authorizeAsAdmin(server)):
            return

        if (server.path == "/admin"):
            AdminManager.__sendFile(server, "/admin/index.html") 
            return
        elif (server.path == "/admin/createUser"): #TODO
            AdminManager.__createUser(server)
            return
        elif (server.path.startswith("/admin/logs")):
            AdminManager.__showLogs(server)
            return 
        elif (server.path.startswith("/admin/deleteLog")):
            AdminManager.__deleteLog(server)
            return
        elif (server.path == "/admin/getActiveLog"):
            AdminManager.__getActiveLog(server)
            return
        elif (server.path == "/admin/getSettings"):
            AdminManager.__getSettings(server)
            return
        elif (server.path == "/admin/restart"):
            AdminManager.__restartServer(server)
            return
        elif (server.path == "/admin/shutdown"):
            AdminManager.__shutDown(server)
            return
        elif (server.path == "/admin/changeConfiguration"):
            AdminManager.__changeConfig(server)
            return
        elif (server.path == "/admin/update"):
            AdminManager.__update(server)
            return
        elif (server.path == "/admin/cheeseRelease"):
            AdminManager.__getRelease(server)
            return
        AdminManager.__sendFile(server, server.path)        
        

    @staticmethod
    def setAuth():
        AdminManager.users = []
        for user in Metadata.admin["adminUsers"]:
            AdminManager.users.append(base64.b64encode(
                bytes('%s:%s' % (user["name"], user["password"]), 'utf-8')).decode('ascii'))

    @staticmethod
    def authorizeAsAdmin(server):
        if (server.headers.get("Authorization") != None):
            for user in AdminManager.users:
                if (server.headers.get("Authorization") == "Basic " + str(user)):
                    return True
        server.do_AUTHHEAD()
        return False


    # PRIVATE METHODS

    @staticmethod
    def __sendFile(server, file):
        file = ResMan.joinPath(ResMan.admin(), *file.split("/")[2:])
        if (not os.path.exists(file)):
            with open(f"{ResMan.error()}/error404.html", "rb") as f:
                CheeseController.sendResponse(server, (f.read(), 404))
            return

        with open(f"{file}", "r", encoding="utf-8") as f:
            CheeseController.sendResponse(server, (bytes(f.read(), "utf-8"), 200), "text/html")

    @staticmethod
    def __createUser(server):
        pass

    @staticmethod
    def __showLogs(server):
        CheeseController.sendResponse(server, Logger.serveLogs(server), "text/html")

    @staticmethod
    def __deleteLog(server):
        args = CheeseController.getArgs(server.path)
        if (not CheeseController.validateJson(["log"], args)):
            CheeseController.sendResponse(server, Error.BadJson)
            return

        log = args["log"]
        path = f"{ResMan.logs()}/{log}"
        if (not os.path.exists(path)):
            CheeseController.sendResponse(server, Error.FileNotFound)
            return

        try:
            os.remove(path)
            response = CheeseController.createResponse({"RESPONSE": "OK"}, 200)
            CheeseController.sendResponse(server, response)
        except Exception as e:
            Logger.fail("Error while removing log", e, silence=False)
            Error.sendCustomError(server, "File was not deleted", 500)


    @staticmethod
    def __getActiveLog(server):
        for root, dirs, files in os.walk(ResMan.logs()):
            activeLog = sorted(files)[-1]
        
        log = ResMan.joinPath(ResMan.logs(), activeLog)
        with open(f"{log}", "r") as f:
            lines = f.readlines()
            min = 0
            if (len(lines) >= 1000): min = len(lines) - 1000
            onlyTable = "".join(lines[min:(min+1000)])
        response = CheeseController.createResponse({"RESPONSE": {"LOG_DESC": activeLog.replace(".html", ""), "LOG": onlyTable}}, 200)
        CheeseController.sendResponse(server, response, "text/html")

    @staticmethod
    def __getSettings(server):
        js = Settings.loadJson()
        CheeseController.sendResponse(server, (bytes(json.dumps(js), "utf-8"), 200), "text/html")

    @staticmethod
    def __restartServer(server):
        Logger.adminInfo(20*"=", silence=False)
        Logger.adminInfo("REQUEST FOR SERVER RESTART SUCCESSFULLY RECIEVED", silence=False)
        Logger.adminInfo("Restart will start in 5 seconds", silence=False)
        time.sleep(5)
        for root, dirs, files in os.walk(ResMan.src()):
            server.server.socket.close()
            time.sleep(5)
            if (os.name == "nt"):
                subprocess.call(f"{sys.executable} \"{ResMan.joinPath(ResMan.src(), files[0])}\"")
            else:
                subprocess.call(f"{sys.executable} \"{ResMan.joinPath(ResMan.src(), files[0])}\"", shell=True)

    @staticmethod
    def __shutDown(server):
        Logger.adminInfo(20*"=", silence=False)
        Logger.adminInfo("REQUEST FOR SERVER SHUT DOWN SUCCESSFULLY RECIEVED", silence=False)
        Logger.adminInfo("Shut down will start in 5 seconds", silence=False)
        time.sleep(5)
        server.server.socket.close()

    @staticmethod
    def __changeConfig(server):
        args = CheeseController.getCookies(server)
        try:
            config = json.loads(args["config"])
            Settings.saveJson(config)
        except Exception as e:
            Logger.fail("ERROR while saving configuration", e)
            Error.sendCustomError(server, "Error while saving configuration", 500)
            return

        Logger.adminInfo("Configuration was updated.", silence=False)
        Logger.adminInfo("Restart to apply changes.", silence=False)
        response = CheeseController.createResponse({"STATUS": "ok"}, 200)
        CheeseController.sendResponse(server, response)
        
    @staticmethod
    def __update(server):
        Logger.adminInfo(20*"=", silence=False)
        Logger.adminInfo("Updating from git", silence=False)
        subprocess.call(f"cd {ResMan.root()}; git pull", shell=True)
        Logger.adminInfo("Project has been updated. Restart to apply changes.", silence=False)
        response = CheeseController.createResponse({"RESPONSE": "OK"}, 200)
        CheeseController.sendResponse(server, response)

    @staticmethod
    def __getRelease(server):
        response = CheeseController.createResponse({"RELEASE": Variables.release}, 200)
        CheeseController.sendResponse(server, response)