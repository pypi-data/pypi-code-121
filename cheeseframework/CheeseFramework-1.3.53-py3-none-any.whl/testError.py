#cheese

class TestError(Exception):

    def __init__(self, value, template, comment):
        self.value = value
        self.template = template
        self.comment = comment

class MockError(Exception):

    def __init__(self, repositoryName, methodName, argName):
        self.repositoryName = repositoryName
        self.methodName = methodName
        self.argName = argName