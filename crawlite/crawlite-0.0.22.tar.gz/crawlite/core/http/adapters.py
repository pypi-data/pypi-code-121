from requests_file import FileAdapter


class CrawliteFileAdapter(FileAdapter):

    def send(self, request, **kwargs):
        resp = super().send(request, **kwargs)
        resp.request = request
        return resp
