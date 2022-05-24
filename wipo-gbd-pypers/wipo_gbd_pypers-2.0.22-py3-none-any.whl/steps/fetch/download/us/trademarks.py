import os
import re
from bs4 import BeautifulSoup
from pypers.steps.base.fetch_step_http import FetchStepHttpAuth
from pypers.utils.utils import ls_dir
from datetime import datetime


class Trademarks(FetchStepHttpAuth):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using HTTP GET"
        ],
        "args":
        {
            "params": [
                {
                    "name": "file_xml_regex",
                    "type": "str",
                    "descr": "regular expression to filter files",
                    "value": ".*"
                },
                {
                    "name": "file_img_regex",
                    "type": "str",
                    "descr": "regular expression to filter files",
                    "value": ".*"
                }
            ],
        }
    }

    def _process_from_local_folder(self):
        # getting files from local dir
        if self.fetch_from.get('from_dir'):
            self.logger.info(
                'getting %s files that match the regex [%s] from %s' % (
                    'all' if self.limit == 0 else self.limit,
                    '%s or %s' % (self.file_xml_regex, self.file_img_regex),
                    self.fetch_from['from_dir']))
            xml_archives = ls_dir(
                os.path.join(self.fetch_from['from_dir'], '*'),
                regex=self.file_xml_regex, limit=self.limit,
                skip=self.done_archives)

            img_archives = ls_dir(
                os.path.join(self.fetch_from['from_dir'], '*'),
                regex=self.file_img_regex % ('.*'), limit=self.limit,
                skip=self.done_archives)
            self.output_files = xml_archives + img_archives
            return True
        return False

    def specific_http_auth_process(self, session):

        page_xml_url = os.path.join(self.page_url, 'dailyxml', 'applications')
        page_img_url = os.path.join(self.page_url, 'application', 'images',
                                    str(datetime.today().year))

        # regex to find xml archives download links
        xml_rgx = re.compile('^[^-]+\.zip', re.IGNORECASE)
        # downloaded xml archvie uid (180101) to get their matching images
        archive_uids = []

        cmd = 'wget -q --retry-connrefused --waitretry=15 ' \
              '--read-timeout=60 --timeout=15 -t 5 %s ' \
              '--directory-prefix=%s'
        # 1- download archives for xml applications
        # --------------------------------------
        count = 0
        marks_page = session.get(page_xml_url, proxies=self.proxy_params)
        marks_dom = BeautifulSoup(marks_page.text, 'html.parser')
        # find marks links
        a_elts = marks_dom.findAll('a', href=xml_rgx)
        a_links = [a.attrs['href'] for a in a_elts]
        a_links.reverse()
        for archive_path in a_links:
            archive_name = os.path.basename(archive_path)
            archive_uid = re.sub(r'\D', '', archive_name)
            archive_uids.append(archive_uid)
            archive_url = os.path.join(page_xml_url, archive_name)
            # it had become increasingly hard to download xml archives
            count, should_break = self.parse_links(archive_name, count, cmd,
                                                   archive_url=archive_url)
            if should_break:
                break

        # 2- download archives for tm images
        # -------------------------------
        file_img_regex = self.file_img_regex % '|'.join(archive_uids)
        img_rgx = re.compile('.*%s' % file_img_regex,
                             re.IGNORECASE)
        marks_page = session.get(page_img_url, stream=True,
                                 proxies=self.proxy_params)
        download_lines = []
        # enough to look in the first 1000 lines
        for line in marks_page.text.splitlines():
            if line:
                if img_rgx.match(line):
                    download_lines.append(line)
        marks_dom = BeautifulSoup(''.join(download_lines), 'html.parser')
        # find marks links
        a_elts = marks_dom.findAll('a', href=img_rgx)
        a_links = [a.attrs['href'] for a in a_elts]

        count = 0
        for archive_path in a_links:
            archive_name = os.path.basename(archive_path)
            archive_url = os.path.join(page_img_url, archive_path)
            count, should_break = self.parse_links(archive_name, count, cmd,
                                                   archive_url=archive_url)
            if should_break:
                break
