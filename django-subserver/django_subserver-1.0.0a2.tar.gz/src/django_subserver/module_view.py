'''
Note - this module is actually completely independent of the rest of django_subserver.
'''

from django import http
from importlib import import_module

_known_methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
def _options(allowed_methods):
    if 'OPTIONS' not in allowed_methods :
        allowed_methods += ['OPTIONS']
    response = http.HttpResponse()
    response['Allow'] = ', '.join(allowed_methods)
    response['Content-Length'] = '0'
    return response

def module_view(name, package=None):
    '''
    Imports the named module, and creates a view from it.

    Helpful if you want to use a "module-per-view" code layout.

    We perform dispatch-by-method, similar to django.views.generic.View

    -------------------------------------------------------------------
    The referenced module may implement:

    handle_auth(request: SubRequest) -> Optional[HttpResponse]
        Will be called before all HTTP methods.
        You can return a response to short-circuit processing.

        We do NOT recommend doing any complex permission checks here.
        Instead, the parent Router should set permission flags (or 
        permission checking functions) on the request. In that case, you 
        can check those flags/functions here, and so can the parent page 
        (so it can determine whether or not to link to us).        

    handle_get
    handle_post
    handle_put
    handle_patch
    handle_delete
    handle_head
    handle_options
    handle_trace
        (request: SubRequest) -> HttpResponse

        We'll call the appropriate function, based on request method.

    -------------------------------------------------------------------
    Note: all the functions we read are prefixed with "handle_".
    This makes it less likely that you'll accidentally define a helper
    function with the same name as an http-method-handler function.

    -------------------------------------------------------------------
    Note: the returned function 
    '''
    module = import_module(name, package)
    methods = {}
    for method_name in _known_methods :
        try :
            methods[method_name] = getattr(module, 'handle_'+method_name)
        except AttributeError :
            pass
    allowed_methods = [name.upper() for name in methods]

    auth = getattr(module, 'handle_auth', lambda sr: None)

    def view(request):
        '''
        Note - we intentionally don't accept url parameters 
        (ie. captured from a Router).
        Anything that needs to interpret url parameters should be a Router,
        in a routers.py file. 
        '''
        early_response = auth(request)
        if early_response :
            return early_response

        mname = request.method.lower()
        try :
            method = methods[mname]
        except KeyError :
            if mname == 'options' :
                return _options(allowed_methods)
            return http.HttpResponseNotAllowed(allowed_methods)
        return method(request)

    return view

def package_view_importer(package):
    '''
    Returns a module_view wrapper which imports modules from the given package.

    Useful if you have all/most of your "view-modules" in a single package.
    '''
    def module_view_from_package(name):
        return module_view('.'+name, package)
    return module_view_from_package
