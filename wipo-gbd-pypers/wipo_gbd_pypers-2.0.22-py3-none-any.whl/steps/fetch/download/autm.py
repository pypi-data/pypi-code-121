from bs4 import BeautifulSoup
from pypers.steps.base.fetch_step_http import FetchStepHttpAuth


class AUTM(FetchStepHttpAuth):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using HTTP with Basic Auth"
        ],
    }

    def specific_http_auth_process(self, session):
        count = 0
        marks_page = session.get(self.page_url, proxies=self.proxy_params,
                                 auth=self.auth)
        marks_dom = BeautifulSoup(marks_page.text, 'html.parser')
        # find marks links
        a_elts = marks_dom.findAll('a', href=self.rgx)
        a_links = [a.attrs['href'] for a in a_elts]

        cmd = 'wget -q --user=%s --password=%s'
        cmd += ' %s --directory-prefix=%s'
        cmd = cmd % (self.conn_params['credentials']['user'],
                     self.conn_params['credentials']['password'],
                     '%s', '%s')
        for archive_name in a_links:
            count, should_break = self.parse_links(archive_name, count, cmd=cmd)
            if should_break:
                break
