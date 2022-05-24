from pypers.steps.base.fetch_step import FetchStep
from requests.auth import HTTPBasicAuth
import requests
import os
import subprocess


class FetchStepHttpAuth(FetchStep):

    from_type = 'from_web'

    def _get_auth(self):
        try:
            self.auth = HTTPBasicAuth(
                self.conn_params['credentials']['user'],
                self.conn_params['credentials']['password'])
        except Exception as e:
            pass
        self.page_url = self.conn_params.get('url', None)

    def parse_links(self, archive_name, count, cmd=None, archive_path=None,
                    callback=None, archive_url=None):
        if not archive_path:
            archive_path = archive_name
        if not archive_url:
            archive_url = os.path.join(self.page_url, archive_path)
        if archive_name in self.done_archives:
            return count, False
        if not self.rgx.match(archive_name):
            return count, False
        if self.limit and count == self.limit:
            return count, True
        archive_dest = os.path.join(self.output_dir, archive_name)

        self.logger.info('>> downloading: %s to %s' % (archive_url, archive_dest))

        if cmd:
            cmd = cmd % (archive_url, self.output_dir)
            retry = 0
            limit_retry = self.cmd_retry_limit
            while True:
                try:
                    subprocess.check_call(cmd.split(' '))
                    break
                except Exception as e:
                    self.logger.warning("Error in %s: %s" % (cmd, e))
                    retry += 1
                    self.logger.info("Retry %s: %s" % (retry, cmd))
                    if retry == limit_retry:
                        raise e
        elif callback:
            callback(archive_dest, archive_url)
        count += 1
        self.output_files.append(archive_dest)
        if self.limit and count == self.limit:
            return count, True
        return count, False

    def specific_process(self):
        self.conn_params = self.fetch_from[self.from_type]

        self.proxy_params = {
            'http': self.meta['pipeline']['input'].get('http_proxy'),
            'https': self.meta['pipeline']['input'].get('https_proxy')
        }

        self._get_auth()

        # login and maintain the session
        with requests.session() as session:
            self.specific_http_auth_process(session)

