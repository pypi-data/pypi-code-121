
import json

from annoying.decorators import render_to
from django.http import Http404, HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

class FlatpageFallbackMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a flatpage for non-404 responses.
        try:
            return flatpage(request)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response

def flatpage(request):

    rows = request.db.view(settings.COUCHDB_FLATPAGES, key=request.path, include_docs=True, limit=1).rows
    if rows:
        row = rows[0]
        if request.is_ajax():
            doc = row.doc.copy()
            doc['text_rendered'] = render_to_string('static_text.html', {'doc': row.doc})
            
            return HttpResponse(json.dumps(doc, ensure_ascii=False, indent=4), mimetype="application/json")
        else:
            return render_to_response(row.doc.get('template', 'static.html'), {'doc': row.doc}, RequestContext(request), mimetype=row.doc.get('content_type', 'text/html'))
    else:
        raise Http404('Page not found')

