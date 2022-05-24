import os

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View

from custom_url.models import CustomUrl

class CustomUrlView(View):
    http_method_names = ['get',]
    
    def get(self, request, *args, **kwargs):
        url = self.kwargs.get('url', None)

        if not url.startswith("/"):
            url = '/' + url
        if not url.endswith("/") and settings.APPEND_SLASH:
            url += '/'
        obj = get_object_or_404(CustomUrl, url=url)
        
        content_type = obj.file_type
        file = obj.file
        file_name = os.path.basename(file.name)

        try:
            return FileResponse(file, content_type=content_type, filename=file_name)
        except:
            raise Http404()