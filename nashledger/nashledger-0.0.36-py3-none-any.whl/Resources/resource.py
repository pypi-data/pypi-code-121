
from erp_sync.APIs.api_format import API
import json
from erp_sync.APIs.utils.generate_code import get_code

class Resource(API):
    
    _client_id = None
    
    _user_id = -1

    _company_id = 1

    _client_type = -1

    _response = {}

    _new_url = ""

    _edit_url = ""

    _read_url = ""

    _delete_url = ""

    _import_url = ""

    _api = None

    QBO = 1
    ZOHO = 2
    SAP = 3
    XERO = 4
    ODOO = 5
    MS_DYNAMICS = 6

    # READ = 0
    # NEW = 1
    # UPDATE = 2

    _resource_id = -1

    @property
    def READ(self):
        return 0

    @property
    def NEW(self):
        return 1

    @property
    def UPDATE(self):
        return 2

    def set_company_id(self, company_id):
        self._company_id = company_id
        return self    

    def set_client_type(self, _client_type):
        self._client_type = _client_type
        return self        
    
    def set_client_id(self, client_id):
        self._client_id = client_id
        return self        
    
    def set_user_id(self, user_id):
        self._user_id = user_id
        return self

    def set_urls(self,urls):
        self.set_new_url(urls.get("new",""))
        self.set_edit_url(urls.get("edit",""))
        self.set_read_url(urls.get("read",""))
        self.set_delete_url(urls.get("delete",""))
        self.set_import_url(urls.get("import",""))
        return self

    def new(self, payload = None, method='POST',endpoint=None, files = None):
        if endpoint is None:
            endpoint = self.get_new_url()

        # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
        self._response = self._exec(payload, method, endpoint, files = files)

        # set response here
        return self

    def edit(self, payload = None, method='PUT',endpoint=None, files = None):
        if endpoint is None:
            endpoint = self.get_edit_url()
        # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
        self._response = self._exec(payload, method, endpoint, files = files)
        return self

    def read(self, payload = None, method='GET',endpoint=None):
        if endpoint is None:
            endpoint = self.get_read_url()

        # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
        self._response = self._exec(payload, method, endpoint)
        return self

    def delete(self, payload = None, method='DELETE',endpoint=None):
        if endpoint is None:
            endpoint = self.get_delete_url()

        # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
        self._response = self._exec(payload, method, endpoint)
        return self
        
    def import_data(self, payload = None, method='GET',endpoint=None):
        if endpoint is None:
            endpoint = self.get_import_url()

        # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
        self._response = self._exec(payload, method, endpoint)
        return self

    def payload(self):
        return {}

    def serialize(self):
        return self

    def response(self):
        return self._response

    def set_response(self,response={}):
        self._response = response
        return self
    
    def set_new_url(self,new_url):
        self._new_url = new_url
        return self
    
    def set_edit_url(self,edit_url):
        self._edit_url = edit_url
        return self
    
    def set_read_url(self,read_url):
        self._read_url = read_url
        return self
    
    def set_delete_url(self,delete_url):
        self._delete_url = delete_url
        return self
    
    def set_import_url(self,import_url):
        self._import_url = import_url
        return self
    
    def get_new_url(self):
        return self._new_url
    
    def get_edit_url(self):
        return self._edit_url
    
    def get_read_url(self):
        return self._read_url
    
    def get_delete_url(self):
        return self._delete_url
    
    def get_import_url(self):
        return self._import_url

    def get_client_id(self):
        return self._client_id
    
    def get_company_id(self):
        return self._company_id
    
    def get_client_type(self):
        return self._client_type
    
    def get_user_id(self):
        return self._user_id
    
    def generate_code(self, length = 6):
        return get_code(length)
    
    # This is the method that will be called execute an A.P.I. request. 
    # Since most of the A.P.I. calls methods are similar, they are to be placed inside this method to avoid code duplication.
    # 
    # It will only accept parameters unique to each A.P.I. request. 
    def _exec(self, payload = None, method='POST', endpoint = "", files = None):
                
        if files is None:
            payload=json.dumps(payload)
        else:
            payload=payload

        # Call the iPay A.P.I. url by passing the variables to the super class method responsible for making requests to A.P.I. endpoints
        # The super class method returns a response that is returned by this method
        return super().api_request(url=f"{super().get_base_url()}{endpoint}", payload=payload, method=method, files=files)