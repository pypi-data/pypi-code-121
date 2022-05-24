from requests.models import Response
from daspython.common.api import ApiMethods, Token


class GetAttributeRequest():
    '''
    The request object to fetch a attribute.

    Attributes
    ----------
        id: int (default None)
            Attribute identifier.
        name: str (default None)
            Attribute name.
        alias: str (default None)
            Attribute alias.
    '''
    id: int = None
    name: str = None
    alias: str = None


class GetAllAttributesRequest(GetAttributeRequest):
    '''
    The request object to fetch a list of attributes.

    Attributes
    ----------
        id: int (default None)
            Attribute identifier.
        name: str (default None)
            Attribute name.
        alias: str (default None)
            Attribute alias.
        tablename: (default None)
            Attribute table name if applicable.
    '''
    tablename: str = None


class AttributeService(ApiMethods):
    '''
    Class that has all methods needed to handle attributes.
    '''

    def __init__(self, auth: Token):
        super().__init__(auth)

    def get(self, request: GetAttributeRequest):
        '''
        Gets an attribute based either on a given:
            - id
            - name or
            - alias

        Parameters
        ----------
        request : GetAttributeRequest
            An instance of the class: GetAttributeRequest that you just need to inform either the id or name or alias.

        Returns
        -------
            A json that represents  the attribute.                           
        '''
        api_url = '/api/services/app/Attribute/Get?'
        return self.get_data(url=api_url, request=request)

    def get_all(self, request: GetAllAttributesRequest = None):
        '''
        Gets either a list of attributes or a filtered list based on the given parameters:
            - id
            - name
            - alias or
            - tablename

        Parameters
        ----------
        request : GetAllAttributesRequest
            An instance of the class: GetAllAttributesRequest that you just need to inform the info of one of its properties.

        Returns
        -------
            A json that represents the list of attributes.                           
        '''
        api_url = '/api/services/app/Attribute/GetAll?'
        return self.get_data(url=api_url, request=request)

    def get_attribute_name(self, id: int) -> str:
        '''
        Gets the attribute name based on the given attribute identifier.

        Parameters
        ----------
            id: int
                Attribute identifier.

        Returns
        -------
        The attribute name.                
        '''
        request = GetAttributeRequest()
        request.id = id
        response = self.get(request)
        if (response != None):
            return response['result']['name']
        else:
            return response

    def get_attribute_id(self, name: str) -> int:
        '''
        Gets the attribute identifier based on the given name.

        Parameters
        ----------
            name: str
                Attribute name.

        Returns
        -------
        The attribute identifier.                
        '''        
        request = GetAttributeRequest()
        request.name = name
        response = self.get(request)
        if (response != None):
            return response['result']['id']
        else:
            return response        
