import json

try:
    # Python 3
    from urllib.parse import urlparse, urlencode
except ImportError:
    # Python 2
    from urlparse import urlparse
    from urllib import urlencode


def build_url(request):
    if request.body:
        parsed = urlparse(request.url)
        if request.headers.get("content-type") == "application/json":
            parsed_body = json.loads(request.body)
        else:
            parsed_body = request.body
        query = "&".join([parsed.query, urlencode({"body": parsed_body})])
        # return '{parsed.scheme}://{parsed.netloc}{parsed.path}?{query}'
        return "{0:s}://{1:s}{2:s}?{3:s}".format(
            parsed.scheme, parsed.netloc, parsed.path, query
        )
    return request.url
