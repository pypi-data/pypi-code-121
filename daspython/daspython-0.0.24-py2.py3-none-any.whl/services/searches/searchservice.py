from daspython.common.api import ApiMethods, Response, Token


class SearchEntriesRequest():
    '''
    The request object needed as search parameters.

    Attributes
    ----------
        attributeId: int (default None)
            Attribute identifier.
        maxresultcount: int (default 10)
            Maximum items expected. The default value is 10.
        skipcount: str (default 0)
            Represents the number of items that should be skipped like a page. The default value is 0 which means, combined with the parameter maxresultcount = 10 a page 0 with 10 items.
        querystring: str (default None)                    
            Your search filter. 
                Example: 'id(56);displayname(64*)' --> Find the item with a identifier equals 56 and the displayname starts with 64.
        sorting: str (default None)                    
            Sorting expression.
                Example: 'displayname asc' --> Sort the result by displayname in ascending order.
    '''
    attributeId: int = None
    maxresultcount: int = 10
    skipcount: int = 0
    querystring: str = None
    sorting: str = None


class SearchService(ApiMethods):
    '''
    The search engine class that should be used to fetch only entries.
    '''

    def __init__(self, auth: Token):
        super().__init__(auth)

    def search_entries(self, body: SearchEntriesRequest) -> Response:
        '''
        Search method to fetch only all types of entries in DAS.

        Parameters
        ----------
        body : SearchEntriesRequest
            An instance of the class: SearchEntriesRequest.

        Returns
        -------
            A json that represents  the search result.                           
        '''
        api_url = '/api/services/app/Search/SearchEntries?'
        response =  self.post_data(url=api_url, body=body)
        return super()._get_entries_response(response)