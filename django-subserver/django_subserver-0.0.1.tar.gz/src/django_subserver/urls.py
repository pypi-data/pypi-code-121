from django import urls
from typing import Any, Mapping, Optional, Sequence

from .base import SubView, SubRequest

def sub_view_urls(sub_view:SubView) -> Sequence[urls.URLPattern]:
    '''
    Provides a means of "installing" a SubView via django urls.

    Returns a list of URLPatterns that will invoke the given SubView
    with an appropriate SubRequest.

    These should be "included" in your url patterns.

    If you "include" under a non-empty prefix, that prefix MUST end with '/'

    You may capture url parameters, and they will be passed to the SubView.
    Any such parameters must be named (not positional), and you cannot 
    name any of them "sub_path" (since we use that).

    Sample usage:

    url_patterns = [
        path('my_sub_app', include(dss.sub_view_urls(my_sub_app))),
    ]
    '''
    def view(request, sub_path='', **other_url_kwargs):
        sub_request = SubRequest(request)

        path = request.path
        handled = path[:len(path)-len(sub_path)]

        if not handled.endswith('/') :
            raise ValueError(f'Invalid parent path: "{handled}". Any prefix you include() sub_view_urls() underneath MUST end in "/".')

        # handled endswith '/', but that '/' is already part of sub_request.parent_path, not sub_request.sub_path
        sub_request.advance(handled[1:])
        return sub_view(sub_request, **other_url_kwargs)

    return [
        # The empty sub_path case
        urls.path('', view),
        # The non-empty sub_path case
        urls.path('<path:sub_path>', view),
    ]
