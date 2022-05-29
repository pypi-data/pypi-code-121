from erp_sync.Resources.customer import Customer
from erp_sync.Resources.company import Company
from erp_sync.APIs.api_format import API
import json

class Client(API, object):

    _resources = {
        "Customer": Customer(),
        "Company": Company()
    }

    # use the nash object to confirm if the user accessin the client is logged in
    _nash = None

    _response = {}

    _client_id = -1

    _company_id = 1

    def __init__(self,nash):
        self._nash = nash
        super().__init__("ClientsAPI", self._nash.get_headers(), self._nash.get_params())

    def resource(self,resource_name):
        # _resource = self._resources[resource_name].set_client_id(self.get_client_id())
        # _resource.set_headers(self._nash.get_headers())
        return self._resources[resource_name].set_client_id(self.get_client_id()).set_headers(self._nash.get_headers())
    
    def get_resources(self):
        return list(self._resources.keys())
    
    def get_client_id(self):
        return self._client_id
    
    def set_client_id(self, client_id):
        self._client_id = client_id
        return self
    
    def set_company_id(self,company_id):
        self._company_id = company_id
        return self
    
    def get_company_id(self):
        return self._company_id
    
    def authenticate(self,client_id = None,payload = None,method='POST',endpoint=""):
        if client_id is None:
            endpoint = f"/clients/{self.get_client_id()}/authenticate"
        else:
            endpoint = f"/clients/{client_id}/authenticate"
            self.set_client_id(client_id)

        
        # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
        self._response = self._exec(payload, method, endpoint)
        
        return self

    def new(self, payload = None, method='POST',endpoint="/clients"):
        # set data to pass to ruby url
        # set response here
        # set client id here
        # self.set_client_id()

        # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
        self._response = self._exec(payload, method, endpoint)
        if self._response["status_code"] == 200:

            self.set_client_id(self._response["response_data"]["id"])


        return self

    def read(self,data):
        # read data from ruby url
        # set response here
        return self
    
    def response(self):
        return self._response
    
    # This is the method that will be called execute an A.P.I. request.
    # Since most of the A.P.I. calls methods are similar, they are to be placed inside this method to avoid code duplication.
    # 
    # It will only accept parameters unique to each A.P.I. request. 
    def _exec(self, payload = None, method='POST', endpoint = ""):

        # Call the iPay A.P.I. url by passing the variables to the super class method responsible for making requests to A.P.I. endpoints
        # The super class method returns a response that is returned by this method
        return super().api_request(url=f"{super().get_base_url()}{endpoint}", payload=json.dumps(payload), method=method)
        



    
