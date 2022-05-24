import re
from urllib import parse as urllib
import hashlib
import requests
import os
import json
import codecs
from datetime import datetime
from bs4 import BeautifulSoup
from pypers.steps.base.step_generic import EmptyStep
from pypers.core.interfaces import db



class Inn(EmptyStep):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch INN list"
        ],
        "args":
        {
            "outputs": [
                {
                    "name": "output_files",
                    "type": "file",
                    "descr": "the download files from the feed"
                },
                {
                    "name": "inns",
                    "type": "dict",
                    "descr": "the proposed and recommended inn lists"
                }
            ],
            "params": [
                {
                    "name": "should_download",
                    "type": "int",
                    "descr": "the flag to force or not the full download (all)",
                    "value": 0
                },
            ],
        }
    }

    langs = {'en': 'English',
             'fr': 'French',
             'es': 'Spanish',
             'ar': 'Arabic',
             'ru': 'Russian',
             'zh': 'Chinese'}

    def _get_inns(self, a_type, list_nb, lang_name):

        fetch_from = self.meta['pipeline']['input']
        if not fetch_from or not fetch_from.get('url'):
            raise Exception('Please set the input of the pipeline url')

        proxy_params = {
            'http':  self.meta['pipeline']['input'].get('http_proxy'),
            'https': self.meta['pipeline']['input'].get('https_proxy')
        }
        # ------------
        xml_param_value = '''
             <INN_Hub_Root INN_Query_Type="HTML" INN_Timestamp="%(timestamp)s" INN_Query_Token="%(token)s" INN_Client_ID="%(client)s">
                 <INN_Hub_Query Logic_Op="MAIN" %(type)s_List="%(number)s">
                     <INN_Query_Content WHO_Lang="%(lang)s">.*</INN_Query_Content>
                 </INN_Hub_Query>
             </INN_Hub_Root>'''
        # ------------


        # get the credentials
        url = fetch_from['url']
        credentials = fetch_from['credentials']
        timestamp = datetime.today().strftime('%Y-%m-%dT%H:%M:%S.0Z')

        # create the token
        md5 = hashlib.md5()
        md5.update(('%s%s.*' % (credentials['password'], timestamp)).encode(
            'utf-8'))
        token = md5.hexdigest()
        with requests.session() as session:
            xml_param = xml_param_value % ({'timestamp': timestamp,
                                            'token': token,
                                            'client': credentials['client'],
                                            'type': a_type[0].upper(),
                                            'number': list_nb,
                                            'lang': lang_name})
            xml_param = ''.join([el.strip()
                                 for el in xml_param.split('\n')])
            xml_param = urllib.urlencode({'INN_Hub_XML': xml_param})
            page = session.get(url, params=xml_param, proxies=proxy_params)
            soup = BeautifulSoup(page.text, 'html.parser')
            inns = soup.select('a[class="INN_Hub"]')
        return inns

    def _has_next(self, a_type, list_nb):
        # check next publication in english
        lang_name = 'English'
        inns = self._get_inns(a_type, list_nb, lang_name)
        self.logger.info('%s List %s : %s entries' % (
            a_type, list_nb, len(inns)))
        return list_nb, len(inns)


    def preprocess(self):
        # pickup self.number from done file
        # Avoid the precheck if we force a full download
        if self.should_download == 1:
            return
        done_file = db.get_done_file_manager().get_done(self.collection)
        done_file = sorted(done_file, key=lambda i: i['process_date'], reverse=True)
        done_lists = [line['archive_name'] for line in done_file]

        done_proposed = [int(re.findall(r'\d+', el[10:]).pop())
                         for el in done_lists if 'proposed' in el]
        done_recommended = [int(re.findall(r'\d+', el[10:]).pop())
                            for el in done_lists
                            if 'recommended' in el]
        if not done_proposed:
            next_proposed = 1
        else:
            next_proposed = sorted(done_proposed).pop() + 1
        if not done_recommended:
            next_recommended = 1
        else:
            next_recommended = sorted(done_recommended).pop() + 1

        self.next_proposed, next_proposed_entries = self._has_next(
            'proposed', next_proposed)
        self.next_recommended, next_recommended_entries = self._has_next(
            'recommended', next_recommended)

        if next_recommended_entries or next_proposed_entries:
            self.should_download = 1
        else:
            self.should_download = 0

    def process(self):
        if self.should_download == 0:
            return
        self.output_files = []
        inns_lists = []
        for type in ['Recommended', 'Proposed']:
            list_nb = 1
            extract_out = os.path.join(self.output_dir, type.lower())
            os.makedirs(extract_out, exist_ok=True)

            # lists by type object
            while True:
                self.logger.info('%s List %s' % (type, list_nb))
                inn_count = 0

                # inns by list number
                inns_list = {'number': list_nb, 'publications': {}, 'type': type}

                for lang_code, lang_name in self.langs.items():
                    inns = self._get_inns(type, list_nb, lang_name)


                    for idx, inn in enumerate(inns):
                        inn_text = inn.text
                        inn_link = inn.get('href')
                        inn_code = urllib.parse_qs(urllib.urlparse(
                            inn_link).query)['code'].pop()

                        # inn publication
                        inns_list['publications'].setdefault(inn_code,
                                                             {})
                        inns_list['publications'][
                            inn_code].setdefault('names', {})
                        inns_list['publications'][
                            inn_code]['names'][lang_code] = inn_text
                        inns_list['publications'][
                            inn_code]['list_entry'] = idx + 1

                    inn_count += len(inns)

                    self.logger.info('  > %s\t:\t%s names' % (
                        lang_name, len(inns)))
                # if all language gave 0 counts
                if inn_count == 0:
                    break
                inns_lists.append(inns_list)

                self.logger.info('\n')
                list_nb += 1

        output_file = os.path.join(
            extract_out, '%s.json' % (datetime.now().strftime("%Y_%m_%d")))
        with codecs.open(output_file, 'wb', 'utf-8') as fh:
            fh.write(json.dumps(inns_lists))
        self.output_files.append(output_file)
