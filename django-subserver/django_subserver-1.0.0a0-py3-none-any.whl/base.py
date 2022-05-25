from abc import ABC
from django.http import HttpRequest, HttpResponse

class SubRequest:
    '''
    HttpRequest wrapper, with the ability to keep track of
    "parent_path" and "sub_path".

    Exposes all of the public attributes of the underlying HttpRequest,
    so in most cases a SubRequest can be used directly where an 
    HttpRequest would have been used.

    We also explicitly endorse the adding of arbitrary data directly to
    SubRequest instances. We have mechanisms in place to prevent the
    accidental shadowing of standard SubRequest or HttpRequest attributes.
    You can also call "clear_data()" to erase any previously added custom
    data (to ensure that the next SubView you delegate to is not dependent
    on that data). Our interface is considered final. We'll never add any 
    more (public) attributes (without changing major version number).
    '''

    # We delegate the getting of these attributes to the underlying HttpRequest
    # Users cannot shadow them on SubRequest instances
    PUBLIC_REQUEST_ATTRIBUTES = [
        'scheme',
        'body',
        'path',
        'path_info',
        'method',
        'encoding',
        'content_type',
        'content_params',
        'GET',
        'POST',
        'COOKIES',
        'FILES',
        'META',
        'headers',
        'resolver_match',

        # methods:
        'get_host',
        'get_port',
        'get_full_path',
        'get_full_path_info',
        'build_absolute_uri',
        'get_signed_cookie',
        'is_secure',
        # 'is_ajax',   # deprecated in 3.1, and removed in 4.0
        'accepts',
        'read',
        'readline',
        '__iter__',
    ]

    # Common dynamically added HttpRequest instance attributes
    # We delegate getting AND setting to underlying HttpRequest
    SETTABLE_REQUEST_ATTRIBUTES = [
        'current_app',
        'urlconf',
        'exception_reporter_filter',
        'exception_reporter_class',
        'session',
        'site',
        'user',
    ]

    def __init__(self, request: HttpRequest): 
        self._request = request
        self._parent_path_length = 1

    @property
    def request(self) -> HttpRequest:
        '''
        Returns the HttpRequest associated with this SubRequest.
        For the most part, you can use a SubRequest instance as if it was
        the underlying HttpRequest, so you shouldn't need this often
        (if at all).
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

        Note that it does NOT clear any of the _settable_request_attributes
        (which are set directly on the underlying HttpRequest).
        '''
        keys = [key for key in self.__dict__ if not key.startswith('_')]
        for key in keys :
            del self.__dict__[key]

    # Delegate getting/setting of various properties to the underlying request
    def __setattr__(self, attr, value):
        '''
        We encourage adding arbitrary data directly onto SubRequest instances.
        Here, we make sure such usage doesn't accidentally shadow class attributes, or standard HTTPRequest attributes.
        We also ensure that attributes don't start with '_', because those 
        are reservered for use internally by the class.
        '''
        def message(attr, reason):
            return f'Illegal attribute: "{attr}"; {reason}'

        if attr.startswith('_') :
            if attr not in ('_request', '_parent_path_length') :
                raise AttributeError(message(attr, 'private attributes (starting with "_") are reserved for internal use by SubRequest'))

        if hasattr(SubRequest, attr):
            raise AttributeError(message(attr, 'cannot shadow SubRequest attributes.'))
        
        if attr in self.PUBLIC_REQUEST_ATTRIBUTES:
            raise AttributeError(message(attr, 'cannot shadow HTTPRequest attributes'))

        if attr in self.SETTABLE_REQUEST_ATTRIBUTES :
            setattr(self._request, attr, value)
        else :
            super().__setattr__(attr, value)
    def __getattr__(self, attr):
        if (
            attr in self.PUBLIC_REQUEST_ATTRIBUTES 
            or attr in self.SETTABLE_REQUEST_ATTRIBUTES 
        ) :
            return getattr(self._request, attr)
        return super().__getattr__(attr)
    def __hasattr__(self, attr):
        if (
            attr in self.PUBLIC_REQUEST_ATTRIBUTES
            or attr in self.SETTABLE_REQUEST_ATTRIBUTES 
        ) :
            return hasattr(self._request, attr)
        return super().__hasattr__(attr)

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