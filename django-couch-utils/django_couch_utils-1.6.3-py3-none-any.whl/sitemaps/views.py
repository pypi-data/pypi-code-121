from django.utils.encoding import smart_str
from django.http import HttpResponse, Http404
from django.template import loader

def sitemap(request, sitemaps):
    urls = []
    for site in sitemaps.values():
        urls.extend(site().get_urls())
    
    xml = smart_str(loader.render_to_string('sitemap.xml', {'urlset': urls}))
    return HttpResponse(xml, mimetype='application/xml')
