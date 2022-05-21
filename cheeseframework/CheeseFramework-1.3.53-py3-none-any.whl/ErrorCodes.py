#cheese

from Cheese.cheeseController import CheeseController
from Cheese.Logger import Logger
from Cheese.httpError import HTTPError
from Cheese.httpServerError import InternalServerError

class Error:
    
    @staticmethod
    def init():
        Error.BadJson = CheeseController.createResponse({"ERROR": "Wrong json structure"}, 400) # Bad request
        Error.OldPass = CheeseController.createResponse({"ERROR": "Old password"}, 401) # Unauthorized
        Error.BadCred = CheeseController.createResponse({"ERROR": "Wrong credentials"}, 401) # Unauthorized
        Error.BadToken = CheeseController.createResponse({"ERROR": "Unable to authorize with this token"}, 401) # Unauthorized
        Error.AccDenied = CheeseController.createResponse({"ERROR": "Access denied"}, 401) # Unathorized
        Error.FileNotFound = CheeseController.createResponse({"ERROR": "File not found"}, 404) # File not found

    @staticmethod
    def sendCustomError(server, code, comment, **errorDesc):
        error = {
                "ERROR": {
                    "NAME": comment,
                    "CODE": code
                    }
            }
        for key in errorDesc.keys():
            error["ERROR"][key] = errorDesc[key]

        response = CheeseController.createResponse(error, code)
        CheeseController.sendResponse(server, response)

    @staticmethod
    def handleError(server, error):
        if (not isinstance(error, HTTPError)):
            Error.logErrorMessage(error)
            error = InternalServerError("An unknown error occured")

        if (server != None):
            Error.sendCustomError(server, error.code, error.name, DESCRIPTION=error.description)

    @staticmethod
    def logErrorMessage(error):
        errorMessage = f"\n{Logger.WARNING}{error.args[0]}{Logger.FAIL}"
        while (len(error.args) > 1):
            error = error.args[1]
            errorMessage += "\n" + 20*"==" + "\n"
            errorMessage += "\n" + f"{Logger.WARNING}{error.args[0]}{Logger.FAIL}"
        Logger.fail(f"{type(error).__name__} occurred: {errorMessage}", False)
        return error
