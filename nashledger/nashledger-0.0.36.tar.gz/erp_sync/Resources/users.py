from erp_sync.Resources.resource import Resource

class Users(Resource):

    urls = {}

    def __init__(self,nash = None):
        if nash is not None:
            super().__init__("UsersAPI", nash.get_headers(), nash.get_params())
            super().set_user_id(nash.get_user_id())
        self._set_urls()

    def _set_urls(self):

        self.urls = {
            "new" : f"/users",
            "edit" : f"/users",
            "read" : f"/users/{super().get_user_id()}",
            "delete" : f"/users",
        }

        super().set_urls(self.urls)

        return self
    
    def edit(self,user_id = None, payload = None):

        self._set_urls()
        
        if user_id is not None:

            self.urls["edit"] = f'{self.urls["edit"]}/{user_id}'

            super().set_urls(self.urls)
        
        return super().edit(payload)
    
    def read(self,user_id = None, payload = None, method='GET',endpoint=None):

        self._set_urls()
        
        if user_id is not None:

            self.urls["read"] = f'{self.urls["new"]}/{user_id}'

            super().set_urls(self.urls)
        
        return super().read(payload, method, endpoint)
    
    def login(self,payload = None, method='POST',endpoint="/auth/login"):

        return super().read(payload, method, endpoint)
    
    def add_client(self,user_id = None, payload = None, method='POST',endpoint="/add_client"):

        self._set_urls()
        
        if user_id is not None:

            self.urls["edit"] = f'{self.urls["edit"]}/{user_id}{endpoint}'
        
        else:
            self.urls["edit"] = f'{self.urls["edit"]}/{super().get_user_id()}{endpoint}'

        super().set_urls(self.urls)

        return super().edit(payload, method)
    
    def remove_client(self,user_id = None, payload = None, method='POST',endpoint="/add_client"):

        self._set_urls()
        
        if user_id is not None:

            self.urls["delete"] = f'{self.urls["delete"]}/{user_id}{endpoint}'
        
        else:
            self.urls["delete"] = f'{self.urls["delete"]}/{super().get_user_id()}{endpoint}'

        super().set_urls(self.urls)

        return super().delete(payload, method)
    
    def add_company(self,user_id = None, payload = None, method='POST',endpoint="/add_company"):

        self._set_urls()
        
        if user_id is not None:

            self.urls["edit"] = f'{self.urls["edit"]}/{user_id}{endpoint}'
        
        else:
            self.urls["edit"] = f'{self.urls["edit"]}/{super().get_user_id()}{endpoint}'
        
        super().set_urls(self.urls)

        return super().edit(payload, method)
    
    def remove_company(self,user_id = None, payload = None, method='POST',endpoint="/remove_company"):

        self._set_urls()
        
        if user_id is not None:

            self.urls["delete"] = f'{self.urls["delete"]}/{user_id}{endpoint}'
        
        else:
            self.urls["delete"] = f'{self.urls["delete"]}/{super().get_user_id()}{endpoint}'

        super().set_urls(self.urls)

        return super().delete(payload, method)