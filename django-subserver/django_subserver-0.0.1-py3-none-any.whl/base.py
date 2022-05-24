from abc import ABC
from django.http import HttpRequest, HttpResponse

class SubRequest:
    '''
    Very similar to HttpRequest, with the ability to keep track of
    "parent_path" and "sub_path".

    SubRequests wrap HttpRequests, and expose most of the important
    HttpRequest properties from the request.

    The wrapped request can be accessed directly, if needed.

    This interface is considered final.
    We'll never add any more (public) attributes.
    Users of SubRequests should feel free to add attributes at will, 
    to pass information from one "sub view" to another.
    '''
    def __init__(self, request: HttpRequest): 
        self._request = request
        self._parent_path_length = 1

    @property
    def request(self) -> HttpRequest:
        '''
        Returns the HttpRequest associated with this SubRequest.
        We have properties to expose the most commonly needed attributes from this request,
        but users can always access the request directly, if needed.
        '''
        return self._request

    @property
    def parent_path(self):
        '''
        Returns the portion of the url path that has already been interpreted.
        Guarantee: 
        parent_path.endswith('/')
        '''
        return self._request.path[:self._parent_path_length]

    @property
    def sub_path(self):
        '''
        Returns the part of the path that has not yet been interpreted.
        Guarantee:
        parent_path + sub_path = request.path
        '''
        return self._request.path[self._parent_path_length:]

    def advance(self, path_portion: str):
        '''
        Note: end users aren't likely to ever need this.
        '''
        if not path_portion.endswith('/') :
            raise ValueError('path_portion must end with "/"')
        if not self.sub_path.startswith(path_portion) :
            raise ValueError('path_portion is not a prefix of sub_path')
        self._parent_path_length += len(path_portion)

    def clear_data(self):
        '''
        Removes all custom data from instance.

        Useful if you want to ensure that the next sub view you delegate to
        is decoupled from previous sub views.
        '''
        keys = [key for key in self.__dict__ if not key.startswith('_')]
        for key in keys :
            del self.__dict__[key]

    def __setattr__(self, attr, value):
        '''
        We encourage adding arbitrary data directly onto SubRequest instances.
        Here, we make sure such usage doesn't accidentally shadow class attributes.
        We also ensure that attributes don't start with '_', because those 
        are reservered for use internally by the class.
        '''
        if attr.startswith('_') :
            if attr not in ('_request', '_parent_path_length') :
                raise AttributeError(f'Private attributes (starting with "_") are not allowed on SubRequest instances. They are reserved for use by the SubRequest class.')
        else :
            if hasattr(SubRequest, attr):
                raise AttributeError(f'Cannot shadow SubRequest attributes/properties. "{attr}" is already defined on SubRequest.')
        super().__setattr__(attr, value)

    # Expose various useful request properties
    @property 
    def headers(self):
        '''Returns self.request.headers'''
        return self._request.headers
    @property 
    def method(self):
        '''Returns self.request.method'''
        return self._request.method
    @property 
    def GET(self):
        '''Returns self.request.GET'''
        return self._request.GET
    @property 
    def POST(self):
        '''Returns self.request.POST'''
        return self._request.POST
    @property 
    def FILES(self):
        '''Returns self.request.FILES'''
        return self._request.FILES

class SubView(ABC):
    '''
    This is just a description of what a "sub view" is.

    A standard django view function takes:
    - an HttpRequest
    - ALL captured url parameters

    A "sub view" is similar. It takes:
    - a SubRequest
    - parameters captured by the parent Router only
    '''
    def __call__(self, request: SubRequest, **captured_params) -> HttpResponse :
        pass