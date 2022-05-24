import csv
from daspython.common.response import HasEntry, HasItems, HasTotal
import uuid
import json
from pathlib import Path
from requests.api import request
from daspython.common.api import ApiMethods, Response, Token
from daspython.services.attributes.attributeservice import AttributeService
from daspython.services.searches.searchservice import SearchEntriesRequest, SearchService
from daspython.services.entryfields.entryfieldservice import DisplayType, EntryFieldService


class InsertRequest():
    '''
    Object with the new entry values.

    Attributes
    ----------
        entry: dictionary
            Reprsents the  { 'field1' : 'value1', 'field2' : 'value2' ... } as an entry content.
    '''
    entry = {}
    attributeId = 0


class UpdateRequest(InsertRequest):
    '''
    Object with the entry values to be updated.

    Attributes
    ----------
        entry: dictionary
            Reprsents the  { 'field1' : 'value1', 'field2' : 'value2' ... } as an entry content.
    '''


class GetEntryByCodeRequest():
    '''
    The request object to fetch an entry by its code.

    Attributes
    ----------
        code: str (default None)
            The code from an entry.
    '''
    code: str = None


class GetEntryRequest():
    '''
    The request object to fetch an entry.

    Attributes
    ----------
        attributeid: int (default None)
            The entry's attribute identifier.
        id: str (default None)
            An entry identifier.
    '''
    attributeid: int = None
    id: str = None


class GetAllEntriesRequest():
    '''
    The request object to fetch a list of entries.

    Attributes
    ----------
        attributeId: int (default None)
            The entries attribute identifier.
        maxresultcount: int (default 10)
            Maximum items expected. The default value is 10.
        sorting: str (default None)                    
            Sorting expression.
                Example: 'displayname asc' --> Sort the result by displayname in ascending order.            
        skipcount: str (default 0)
            Represents the number of items that should be skipped like a page. The default value is 0 which means, combined with the parameter maxresultcount = 10 a page 0 with 10 items.
        attributename: str
            If you don't know the attribute identifier you may use the attribute name instead.
        attributealias: str            
            Other alternative if you don't know either the attribute name or the attribute identifier.
        querystring: str (default None)                    
            Your search filter. 
                Example: 'id(56);displayname(64*)' --> Find the item with a identifier equals 56 and the displayname starts with 64.
    '''
    attributeid: int = None
    maxresultcount: int = 10
    sorting: str = None
    skipcount: int = 0
    attributename: str = None
    attributealias: str = None
    querystring: str = None


class GetEntryRelationsRequest():
    '''
    The request object to fetch a list of entries with either its children or parents.

    Attributes
    ----------
        attributeId: int (default None)
            The entries attribute identifier.
        maxresultcount: int (default 10)
            Maximum items expected. The default value is 10.
        sorting: str (default None)                    
            Sorting expression.
                Example: 'displayname asc' --> Sort the result by displayname in ascending order.            
        skipcount: str (default 0)
            Represents the number of items that should be skipped like a page. The default value is 0 which means, combined with the parameter maxresultcount = 10 a page 0 with 10 items.
        attributename: str
            If you don't know the attribute identifier you may use the attribute name instead.
        attributealias: str            
            Other alternative if you don't know either the attribute name or the attribute identifier.
        querystring: str (default None)                    
            Your search filter. 
                Example: 'id(56);displayname(64*)' --> Find the item with a identifier equals 56 and the displayname starts with 64.
        relationtype: int               
            1 - Parents and 2 - Children.
        deeplevel: int
            Defines the maximum level of relations to be load on your request.            
    '''
    attributeid: int = None
    attributename: str = None
    attributealias: str = None
    attributetablename: str = None
    sorting: str = None
    maxresultcount: int = 10
    skipcount: int = 0
    relationtype: int = 1
    deeplevel: int = 1

class GetEntryResponse(HasEntry):
    pass

class EntryService(ApiMethods):
    def __init__(self, auth: Token):
        super().__init__(auth)

    def get_all(self, request: GetAllEntriesRequest) -> Response:
        '''
        Get all entries based on the request parameter values.

        Parameters
        ----------
        request : GetAllEntriesRequest
            An instance of the class: GetAllEntriesRequest.

        Returns
        -------
            A json that represents  a list of entries.                           
        '''
        api_url = '/api/services/app/Entry/GetAll?'
        response = self.get_data(url=api_url, request=request)
        return super()._get_entries_response(response)

    def get_entry_by_code(self, code: str) -> GetEntryResponse:
        '''
        Get an entry by its code.

        Parameters
        ----------
        code : str
            An give code from an entry.

        Returns
        -------
            A json that represents  an entry.                           
        '''
        api_url = '/api/services/app/Entry/GetEntryByCode?'
        request = GetEntryByCodeRequest()
        request.code = code
        response =  self.get_data(url=api_url, request=request)
        
        if (response == None):
            return None

        if (response.get('result') == None):
            return None

        result = GetEntryResponse()            
        result.entry = response['result'].get('entry')
        return result


    def get_entry_by_name(self, name: str, attribute_name: str):
        '''
        Get an entry by its name.

        Parameters
        ----------
        name : str
            An given name from an entry.

        Returns
        -------
            A json that represents  an entry.                           
        '''
        search = SearchService(self.token)
        request = SearchEntriesRequest()

        attribute = AttributeService(self.token)
        attribute_id = attribute.get_attribute_id(attribute_name)

        request.attributeId = attribute_id
        request.querystring = f'displayname({name})'

        response = search.search_entries(request)

        if (response == None):
            return None

        if (response.total == 0):
            return None

        return response.items[0]

    def get(self, request: GetEntryRequest):
        '''
        Get an entry.

        Parameters
        ----------
        request : GetEntryRequest
            An instance of the class: GetEntryRequest.

        Returns
        -------
            A json that represents  an entry.                           
        '''
        api_url = '/api/services/app/Entry/Get?'
        return self.get_data(url=api_url, request=request)

    def get_entries_level(self, body: GetEntryRelationsRequest):
        '''
        Get all entries based on the body parameter values and includes either its children or parents based on  the given relation type.

        Parameters
        ----------
        request : GetEntryRequest
            An instance of the class: GetEntryRelationsRequest.

        Returns
        -------
            A json that represents a list of entries.                           
        '''
        api_url = '/api/services/app/Entry/GetAllLevels?'
        return self.post_data(url=api_url, body=body)

    def create(self, body: InsertRequest) -> str:
        '''
        Creates a new entry.

        Parameters
        ----------
        body: InsertRequest
            Represents the entry content that will be used to create a new one. Please see also: InsertRequest.

        Returns
        -------
            The new entry's indentifier.
        '''
        print("creating")
        body.entry['id'] = str(uuid.uuid1())
        body.attributeId = body.entry["attributeid"]
        del body.entry["attributeid"]
        api_url = '/api/services/app/Entry/Create'
        response =  self.post_data(url=api_url, body=body)
        return response['result']

    def update(self, body: UpdateRequest):
        '''
        Updates a new entry.

        Parameters
        ----------
        body: UpdateRequest
            Please see also: UpdateRequest.

        Returns
        -------
            The updated entry's indentifier.
        '''
        api_url = '/api/services/app/Entry/Update'
        response = self.put_data(url=api_url, body=body)
        return response['result']

    def delete_entry(self, id, attributeId):
        '''
        Deletes an entry.

        id: str
            Enty's identifier. 

        attributeId: int
            Enty's attribute identifier.          

        Returns
        -------
            True if the entry was deleted successfully.
        '''
        api_url = f'/api/services/app/Entry/Delete?Id={id}&AttributeId={attributeId}'
        response = self.delete_data(url=api_url)
        return response['result']

    def get_entry_id(self, name: str, attribute_name: str = None, attribute_id: int = None) -> str:
        '''
        Gets the entry identifier based on its name and attribute.

        Parameters
        ----------
            name:str
                Entry's name.
            attribute: str
                Entry's attribute name.

        Returns
        -------
            `str`: Entry identifier.
        '''
        attribute_service = AttributeService(self.token)

        if (attribute_id == None):
            attribute_id = attribute_service.get_attribute_id(attribute_name)

        if (attribute_id == None):
            return None

        search = SearchService(self.token)
        request = SearchEntriesRequest()
        request.querystring = f'displayname({name})'
        request.maxresultcount = 1
        request.attributeId = attribute_id
        response = search.search_entries(request)

        if (response == None or response.total == 0):
            return None

        return response.items[0]['id']

    def create_csv_template(self, attributeName: str, file_name: str = None):

        service = AttributeService(self.token)
        id = service.get_attribute_id(attributeName)

        path = Path(
            f'{attributeName if None == file_name else file_name }.csv')

        service = EntryFieldService(self.token)
        response = service.get_all(id, DisplayType.FORM)

        customdata_list = list(
            map(lambda kv: (kv['column'], kv['customData']), response.items))

        remove_list = list(
            filter(lambda x: (x[1] != None and 'readonly' in x[1]), customdata_list))
        remove_list = list(map(lambda x: x[0], remove_list))
        remove_list.append('6')
        remove_list.append('code')

        header_list = sorted(
            response.items, key=lambda field: field['y'])
        header_list = list(map(lambda kv: kv['column'], header_list))

        header_list = list(
            filter(lambda x: (not x in remove_list), header_list))

        path.write_text(','.join(header_list), 'utf-8')

    def _get_customdata_fields(self, attributeId: int, displayType: DisplayType):
        service = EntryFieldService(self.token)
        fields = service.get_all(attributeId, displayType)
        customdata_list = list(
            map(lambda kv: (kv['column'], kv['customData']), fields.items))
        customdata_list = list(
            filter(lambda x: (x[1] != None), customdata_list))
        return customdata_list

    def _get_customdata_values(self, customdata_fields, entry) -> any:

        service = EntryService(self.token)

        for customdata in customdata_fields:
            if (customdata[0] in entry.keys() and 'datasource' in customdata[1]):
                datasource = json.loads(customdata[1])
                if ('attributeId' in datasource['datasource']):
                    attribute_id = datasource['datasource']['attributeId']
                    entry[customdata[0]] = service.get_entry_id(
                        entry[customdata[0]], attribute_id=attribute_id)

        return entry

    def _get_entry(self, header, row) -> any:
        entry = {}
        for index, h in enumerate(header):
            entry[h] = row[index]

        return entry

    def insert_entries_from_csv(self, csv_file: str, attribute: str):

        new_entries = []
        row_num = 0
        header = None

        with open(csv_file) as reader_file:

            reader = csv.reader(reader_file)

            for r in reader:
                if (row_num == 0):
                    header = r
                else:
                    entry = self._get_entry(header, r)
                    new_entries.append(entry)

                row_num += 1

        service = AttributeService(self.token)
        attribute_id = service.get_attribute_id(attribute)

        customdata_fields = self._get_customdata_fields(
            attribute_id, DisplayType.FORM)

        for entry in new_entries:
            entry = self._get_customdata_values(customdata_fields, entry)
            entry['attributeid'] = attribute_id
            request = InsertRequest()
            request.entry = entry
            self.create(request)
