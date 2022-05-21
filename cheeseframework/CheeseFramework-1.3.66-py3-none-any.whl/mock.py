#cheese

from Cheese.mockManager import MockManager

class Mock:

    def __init__(self, repositoryName):
        self.whenReturns = {}
        self.catch = {}
        self.repoName = repositoryName
        MockManager.setMock(self)

    def whenReturn(self, methodName, response, **kwargs):
        """
        methodName - name of method which will be mocked
        response - response which mocked return will return
        kwargs - dict of arguments singalizing that this is THE case 
        """
        if (methodName not in self.whenReturns.keys()):
            self.whenReturns[methodName] = []
        self.whenReturns[methodName].append(
            {
                "RESPONSE": response,
                "KWARGS": kwargs
            }
        )

    def catchArgs(self, pointer, argName, methodName, **kwargs):
        """
        pointer - id of object which will be filled with return 
        methodName - name of method which will be cached
        """
        if (methodName not in self.catch.keys()):
            self.catch[methodName] = []
        self.catch[methodName].append(
            {
                "POINTER": pointer,
                "ARG_NAME": argName,
                "KWARGS": kwargs
            }
        )

class ServerMock:

    def __init__(self, **kwargs):

        for key in kwargs.keys():
            setattr(self, key, kwargs[key])