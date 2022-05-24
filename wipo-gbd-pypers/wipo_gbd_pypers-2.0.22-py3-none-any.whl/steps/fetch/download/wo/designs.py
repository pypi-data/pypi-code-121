import os
import re
import json
import requests

from pypers.steps.fetch.download.dir import Dir


class Designs(Dir):

    def is_published_in_bulletin(self, archive):
        archive_name = os.path.basename(archive)
        (he_week, he_year) = self.he_week_year(archive_name)
        bulletin_api_byyear = self.bulletin_api % he_year
        with requests.session() as session:
            response = session.get(bulletin_api_byyear,
                                   proxies=self.proxy_params)
            published_bulletins = json.loads(response.content)

        # ["46 - 15.11.2019","45 - 08.11.2019","44 - 01.11.2019", ... ]
        for bull in published_bulletins:
            match = re.search('(?P<week>\d{2}) - .*(?P<year>\d{4})', bull)
            (pub_week, pub_year) = (match.group('week'), match.group('year'))
            if (pub_week, pub_year) == (he_week, he_year):
                return True
        return False

    def he_week_year(self, he_name):
        # HE201947_ST96
        match = re.search('HE(?P<year>\d{4})(?P<week>\d{2})', he_name)
        return match.group('week'), match.group('year')

    def postprocess(self):
        self.bulletin_api = self.meta['pipeline']['input'].get('bulletin_api')
        self.proxy_params = {
            'http': self.meta['pipeline']['input'].get('http_proxy'),
            'https': self.meta['pipeline']['input'].get('https_proxy')
        }

        self.output_files = list(filter(self.is_published_in_bulletin,
                                        self.output_files))
