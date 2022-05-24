import os
import shutil

from bs4 import BeautifulSoup
from pypers.steps.base.fetch_step_http import FetchStepHttpAuth


class Trademarks(FetchStepHttpAuth):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using HTTP with Basic Auth"
        ],
    }

    def specific_http_auth_process(self, session):
        count = 0

        base_url = self.conn_params['burl']

        payload = self.conn_params['payload']

        marks_page = session.post(self.page_url, data=payload)
        marks_dom = BeautifulSoup(marks_page.text, 'html.parser')

        a_elts = marks_dom.findAll('a', href=self.rgx)
        a_links = ['%s%s' % (base_url, a['href']) for a in a_elts]
        a_names = [os.path.basename(a['href']) for a in a_elts]

        a_tuples = list(zip(a_names, a_links))

        def link_downloader(archive_dest, archive_url, *args, **kwargs):
            with open(archive_dest, 'wb') as f:
                r = session.post(archive_url, stream=False, data=payload)
                f.write(r.content)

        for (archive_name, archive_url) in a_tuples:
            count, should_break = self.parse_links(archive_name, count,
                                                   archive_url=archive_url,
                                                   callback=link_downloader)
            if should_break:
                break