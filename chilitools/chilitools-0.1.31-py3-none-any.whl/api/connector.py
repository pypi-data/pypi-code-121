import requests
from datetime import datetime

from chilitools.api import endpoints
from chilitools.api.response import ChiliResponse
from chilitools.utilities.backoffice import getBaseURL, getRequestURL, getEnviormentName
from chilitools.utilities.logger import getLogger
from chilitools.utilities.file import checkForFile, writeFile, readFile
from chilitools.utilities.errors import ErrorHandler
from chilitools.settings.config import CONNECTOR_LOG_FILE, APIKEY_FILE


class ChiliConnector:
    def __init__(self, backofficeURL: str, withLogging: bool = False, forceKeyRegen: bool = False):

        # Backoffice URL Validation should have happend well before this part
        self.backofficeURL = backofficeURL
        self.enviroment = getEnviormentName(backofficeURL=backofficeURL)
        self.baseURL = getBaseURL(backofficeURL=backofficeURL)
        self.requestURL = getRequestURL(backofficeURL=backofficeURL)

        # Reuse API keys or force new API key every call
        self.forceKeyRegen = forceKeyRegen

        # Request/Connector logging
        if withLogging:
            self.logger = getLogger(fullPath=CONNECTOR_LOG_FILE)
            self.logging = True
        else:
            self.logging = False

        # Endpoints
        self.resources = endpoints.Resources(self)
        self.system = endpoints.System(self)
        self.documents = endpoints.Documents(self)

    def makeRequest(self, method: str, endpoint: str, headers: dict = None, queryParams: dict = None, json: dict = None, authRequired: bool = True) -> ChiliResponse:

        requestURL = self.requestURL + endpoint

        requestHeaders = { "accept":"*/*" }

        # Get API key if Auth is required
        if authRequired:
            apiKey = self.getAPIKey()
            requestHeaders['API-KEY'] = apiKey

        if headers is not None:
            for header, value in headers.items():
                requestHeaders[header] = value

        requestQueryParams = {}

        if queryParams is not None:
            for param, value in queryParams.items():
                requestQueryParams[param] = value

        method = method.lower()

        if json is None:
            json = {}

        if method == 'get':
            resp = requests.get(url=requestURL, headers=requestHeaders, params=requestQueryParams, json=json)
        elif method == 'post':
            resp = requests.post(url=requestURL, headers=requestHeaders, params=requestQueryParams, json=json)
        elif method == 'delete':
            resp = requests.delete(url=requestURL, headers=requestHeaders, params=requestQueryParams, json=json)
        elif method == 'put':
            resp = requests.put(url=requestURL, headers=requestHeaders, params=requestQueryParams, json=json)

        request = {'url':requestURL, 'method':method, 'headers':requestHeaders, 'queryParams':requestQueryParams, 'body':json}
        request['body'] = json
        response = ChiliResponse(resp)

        if self.logging:
            self.logger.info({'request':request, 'response':response.asDict()})

        return response


    def getAPIKey(self) -> str:
        genKey = True

        if checkForFile(APIKEY_FILE):
            try:
                apiKeys = readFile(fileName=APIKEY_FILE, isJSON=True)
            except:
                apiKeys = {}
        else:
            print(f"Key file not found, creating one...")
            apiKeys = {}

        if self.backofficeURL in apiKeys:
            if datetime.now() < datetime.fromisoformat(apiKeys[self.backofficeURL]['validTill']):
                key = apiKeys[self.backofficeURL]['key']
                genKey = False
            else:
                print(f"Key found for {self.backofficeURL} is expired, generating a new one...")
        else:
            print(f"Key not found for {self.backofficeURL}, generating one...")

        # Regenerate key if requested
        if self.forceKeyRegen: genKey = False

        if genKey:
            key = self.system.GenerateApiKey()
            if key == ErrorHandler().getError('GENAPIKEY'):
                return ErrorHandler().getError('GENAPIKEY')
            # Date format checking
            validTill = key['@validTill'].replace(' ', 'T').replace('Z', '')
            apiKeys[self.backofficeURL] = {'key':key['@key'], 'validTill':validTill}
            print(f"Successfully generated API key for {self.backofficeURL}")

        # Save key file
        writeFile(fileName=APIKEY_FILE, data=apiKeys, isJSON=True)
        return apiKeys[self.backofficeURL]['key']

    def getXMLFromID(self, resourceType: str, id: str) -> str:
        if resourceType == 'document':
            pass
        if resourceType == 'pdfsettings':
            pass

    def getBackofficeURL(self) -> str:
        return self.backofficeURL

    def getRequestURL(self) -> str:
        return self.requestURL

    def getEnvironment(self) -> str:
        return self.enviroment

    def getLogs(self) -> dict:
        return self.logs

    def __repr__(self) -> str:
        return self.asDict()

    def __str__(self) -> str:
        return f'ChiliConnector(backofficeURL={self.backofficeURL}, enviroment={self.enviroment}, baseURL={self.baseURL}, requestURL={self.requestURL}, logs={self.logs})'

    def asDict(self) -> dict:
        return {"backofficeURL":self.backofficeURL, "enviroment":self.enviroment, "baseURL":self.baseURL, "requestURL":self.requestURL, "logs":self.logs}

