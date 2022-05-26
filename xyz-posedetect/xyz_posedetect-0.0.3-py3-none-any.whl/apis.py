# -*- coding:utf-8 -*-
from __future__ import division

from django.http import FileResponse
from xyz_restful.mixins import BatchActionMixin
from . import models, serializers
from rest_framework import viewsets, decorators, response
from xyz_restful.decorators import register


@register()
class VideoViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Video.objects.all()
    serializer_class = serializers.VideoSerializer
    search_fields = ('source_url', 'name')
    filter_fields = {
        'id': ['in', 'exact'],
        'create_time': ['range']
    }
    ordering_fields = ('is_active', 'create_time',)

    @decorators.action(['GET', 'PATCH'], detail=True)
    def frames(self, request, pk):
        from xyz_util.mongoutils import model_get_and_patch
        return model_get_and_patch(self, field_names=['frames', 'parts'])


    @decorators.action(['GET'], detail=False)
    def proxy(self, request):
        url = request.query_params.get('url')
        try:
            from urllib.parse import urlsplit
        except:
            from urlparse import urlsplit
        from xyz_util.crawlutils import http_get
        ps = urlsplit(url)
        referer = request.GET.get('referer') or '%s://%s' % (ps.scheme, ps.netloc)
        r = http_get(url, proxy=False, referer=referer)
        return FileResponse(
            r.iter_content(FileResponse.block_size),
            content_type=r.headers['Content-Type'],
        )
