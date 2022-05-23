from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class LDPPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        links = []
        for url, label in ((previous_url, 'prev'), (next_url, 'next')):
            if url is not None:
                links.append('<{}>; rel="{}"'.format(url, label))

        headers = {'Link': ', '.join(links)} if links else {}
        return Response(data, headers=headers)
