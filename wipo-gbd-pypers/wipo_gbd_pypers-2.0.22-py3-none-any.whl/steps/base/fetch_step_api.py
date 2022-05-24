from pypers.steps.base.fetch_step import FetchStep
import os
import requests
from pypers.utils.download import retry


class FetchStepAPI(FetchStep):

    from_type = 'from_api'

    def get_connections_info(self):
        api_url = os.path.join(self.conn_params['url'], self.api)
        headers = None
        return api_url, headers

    def get_updates(self, session, url, proxies=None, headers=None,
                    postprocess=None):

        # retry 6 times with a delay of 3secs * n for every n trial
        @retry(Exception, tries=self.http_get_retries,
               delay=self.http_get_delay, backoff=self.http_get_backoff)
        def _get_updates(session, url, proxies=None, headers=None,
                         postprocess=None):
            response = session.get(url, proxies=proxies, headers=headers)
            if not response.status_code == 200:
                raise Exception(response.content)
            if postprocess:
                return postprocess(response.content)
            return response.content
        return _get_updates(session, url, proxies, headers, postprocess)

    def specific_process(self):
        self.conn_params = self.fetch_from[self.from_type]

        self.proxy_params = {
            'http': self.meta['pipeline']['input'].get('http_proxy'),
            'https': self.meta['pipeline']['input'].get('https_proxy')
        }

        self.api_url, self.headers = self.get_connections_info()

        self.intervals = self.get_intervals()

        self.output_files = []
        with requests.session() as session:
            self.specific_api_process(session)
