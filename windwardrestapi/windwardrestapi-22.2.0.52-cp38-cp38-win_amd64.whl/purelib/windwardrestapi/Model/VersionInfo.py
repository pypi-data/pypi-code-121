
import windwardrestapi.Model.VersionNumbers as vn

_VERSION_PATH = "v2/version"
_DOCUMENT_PATH = "v2/document"
_HEADERS = {'Content-Type': 'application/json;charset=UTR-8',
            'Accept': 'application/json'}
class VersionInfo():

    def __init__(self, jsonResp):
        """
        The REST Engine service version.
        """
        self._serviceVersion = jsonResp.json()["ServiceVersion"]
        """
        The document Generation Engine version.
        """
        self._engineVersion = jsonResp.json()["EngineVersion"]
        """
        The API version on the server the client is talking to.
        """
        self._serverApiVersion = jsonResp.json()["ServerApiVersion"]
        """
        The API version on this client. If the server API 2.1.x != the client 2.1.x (the x part can differ, the communication
        is likely going to be a problem).
        """
        self._clientApiVersion = vn.VersionNumbers.CLIENT_VERSION
      
    """
     The REST Engine service version
    """
    def getServiceVersion(self):
        return self._serviceVersion

    '''
    The Document Generation Engine version
    '''
    def getEngineVersion(self):
        return self._engineVersion

    '''
    The API version on the server side
    '''
    def getServerApiVersion(self):
        return self._serverApiVersion

    '''
    The API version on the server side
    '''
    def getClientApiVersion(self):
        return self._clientApiVersion

    def toString(self):
        return 'Service Version: ' + self._serviceVersion + '\nEngine Version: ' + self._engineVersion + "\nServer Api Version: " + self._serverApiVersion + "\nClient Api Version: " + self._clientApiVersion



