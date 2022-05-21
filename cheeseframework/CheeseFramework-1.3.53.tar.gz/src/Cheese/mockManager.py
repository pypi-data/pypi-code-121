#cheese

from Cheese.testError import MockError

class MockManager:

    mocks = {}

    @staticmethod
    def setMock(mock):
        MockManager.mocks[mock.repoName.upper()] = mock

    @staticmethod
    def returnMock(repositoryName, methodName, kwargs):

        if (repositoryName.upper() in MockManager.mocks.keys()):
            mock = MockManager.mocks[repositoryName.upper()]

            if (methodName in mock.whenReturns.keys()): # try to find whenReturn
                method = mock.whenReturns[methodName]

                for ret in method:
                    if (kwargs == ret["KWARGS"]):
                        return MockManager.prepareResponse(ret["RESPONSE"])

            if (methodName in mock.catch.keys()): # try to find catch
                method = mock.catch[methodName]
                
                for catch in method:
                    for key in catch["KWARGS"].keys(): # runs through all condition arguments
                        if (key not in kwargs.keys()):
                            raise MockError(repositoryName, methodName, key)

                        if (kwargs[key] != catch["KWARGS"][key]): # if any of conditions is not acomplished
                            continue

                    if (catch["ARG_NAME"] not in kwargs): # if cached argument is not in kwargs of real method
                        raise MockError(repositoryName, methodName, catch["ARG_NAME"])

                    pointer = catch["POINTER"]
                    pointer.setValue(kwargs[catch["ARG_NAME"]])
        
        return None

    def prepareResponse(response):
        newResponse = response
        if (type(response) == list): #list
            newResponse = []
            for res in response:
                newResponse.append(MockManager.prepareResponse(res))
        elif (type(response) == tuple): # tuple
            for i, res in enumerate(response):
                newResponse[i] = MockManager.prepareResponse(res)
        elif (type(response) == dict): # dictionary
            for key in response.keys():
                newResponse[key] = MockManager.prepareResponse(response[key])
        elif (response.__class__.__name__ == "Pointer"):
            newResponse = MockManager.prepareResponse(response.getValue())

        return newResponse
            