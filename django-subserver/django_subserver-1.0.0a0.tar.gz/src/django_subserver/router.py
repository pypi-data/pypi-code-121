from django.http import HttpResponse, Http404
from importlib import import_module
from typing import Any, Mapping, Optional, Sequence, Union

from .base import SubRequest, SubView
from .pattern import Pattern

ViewSpec = Union[SubView, str]
def _get_view(owning_class, view_spec):
    '''
    A "ViewSpec" is either a sub view, or a string that refers to a SubView class
    (in 'package.module.MyClass' or 'MyClass' format).

    If a string is given, and no package/module is included, the module
    will be inferred to be the same as the module of the class
    that used the ViewSpec.

    The whole purpose of this is so that you can declare your Routers in a single
    module, in "top-down" order. IE:

        class root_router(Router):
            routes = {
                'admin/': 'admin_router',
                 ...
            }
        class admin_router(Router):
            ...
        ...

    In that case, root_router can't just say:
        'admin/': admin_router()
    because admin_router isn't defined yet.
    '''
    if not isinstance(view_spec, str) :
        return view_spec

    try :
        module, cls = view_spec.rsplit('.', 1)
    except ValueError :
        module = owning_class.__module__
        cls = view_spec

    module = import_module(module)
    cls = getattr(module, cls)
    return cls()

class Router(SubView):
    '''
    Subclasses will want to set one or more of:

    - root_view
        called when sub_path == ''
    - routes
        mapping of (sub_path) patterns to sub views
    - cascade
        list of sub views to try
        if any of them do _not_ raise Http404, we'll return whatever they do
    - path_view
        called when sub_path is non-empty, and none of the above match/return a response

    Subclasses may also want to override prepare and/or dispatch.
    '''
    root_view: Optional[SubView] = None
    routes: Mapping[str, ViewSpec] = dict()
    cascade: Sequence[ViewSpec] = []
    path_view: Optional[SubView] = None

    def prepare(self, request: SubRequest, **captured_params:Any) -> Optional[HttpResponse] :
        '''
        If you receive any captured_params, you probably want to interpret and
        attach to request.

        You can perform auth here. 
        You may return an HttpResponse to prevent any further processing.

        Note - captured_params came from the _parent_ router/view,
        not from anything we match on sub_path.
        '''
        pass

    def dispatch(self, request:SubRequest, view:SubView) -> HttpResponse :
        '''
        Subclasses may override to provide response 
        manipulation or exception handling.
        '''
        return view(request)

    # Not to be overriden by sub classes
    def __init__(self):
        self.routes = [
            # TODO - implement Pattern
            (Pattern(pattern), _get_view(self.__class__, view_spec))
            for pattern, view_spec in self.__class__.routes.items()
        ]
        self.cascade_to = [
            _get_view(self.__class__, view_spec)
            for view_spec in self.__class__.cascade
        ]
    def __call__(self, request:SubRequest, **captured_params:[Any]) -> HttpResponse :
        possible_response = self.prepare(request, **captured_params)
        if possible_response :
            return possible_response
        return self.dispatch(request, self._route)
    def _route(self, request):
        if not request.sub_path and self.root_view :
            return self.__class__.root_view(request)
        for pattern, view in self.routes :
            try :
                match, captures = pattern.match(request.sub_path)
            except ValueError :
                continue
            else :
                request.advance(match)
                return view(request, **captures)
        for view in self.cascade_to :
            try :
                return view(request)
            except Http404 :
                continue
        if request.sub_path and self.path_view :
            return self.__class__.path_view(request)
        raise Http404()
