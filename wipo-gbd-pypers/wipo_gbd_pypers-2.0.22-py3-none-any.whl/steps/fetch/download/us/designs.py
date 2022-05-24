import os
from bs4 import BeautifulSoup
from pypers.steps.base.fetch_step_http import FetchStepHttpAuth
from datetime import datetime


class Designs(FetchStepHttpAuth):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using HTTP GET"
        ],
        "args":
        {
            "params": [
                {
                    "name": "archive_regex",
                    "type": "str",
                    "descr": "regular expression to filter files",
                    "value": "I(\\d{8})\\.tar"
                }
            ],
        }
    }

    def _process_from_local_folder(self):
        self.file_regex = self.archive_regex

        return super(Designs, self)._process_from_local_folder()

    def specific_http_auth_process(self, session):
        count = 0
        url = os.path.join(self.page_url, str(datetime.today().year))
        archives_page = session.get(url, proxies=self.proxy_params)
        archives_dom = BeautifulSoup(archives_page.text, 'html.parser')
        # find marks links
        a_elts = archives_dom.findAll('a', href=self.rgx)
        a_links = [a.attrs['href'] for a in a_elts]
        cmd = 'wget -q -c --retry-connrefused --waitretry=15 ' \
              '--read-timeout=120 --timeout=30 -t 10 %s ' \
              '--directory-prefix=%s'
        for archive_path in a_links:
            archive_name = os.path.basename(archive_path)
            archive_url = os.path.join(url, archive_name)
            count, should_break = self.parse_links(archive_name, count, cmd,
                                                   archive_url=archive_url)
            if should_break:
                break
