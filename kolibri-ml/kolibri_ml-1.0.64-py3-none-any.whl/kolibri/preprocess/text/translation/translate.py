
import os
import json, re
import requests
import time
from kolibri.preprocess.text.translation import utils
from kolibri.preprocess.text.translation.constants import (
    LANGCODES, LANGUAGES, TRANSLATE_API, RPCIDS, TRANSLATEURL
)
from kolibri.preprocess.text.translation.models import Translated, Detected
from urllib.parse import quote, urlencode

class Translator:

    def __init__(self, host=TRANSLATE_API, proxies=None, timeout=None,
                retry=3, sleep=5, retry_messgae=False):

        self.host = host if 'http' in host else 'https://' + host
        self.rpcids = RPCIDS
        self.transurl = TRANSLATEURL
        if proxies is not None:
            self.proxies = proxies
        else:
            self.proxies = None
        
        if timeout is not None:
            self.timeout = timeout

        self.retry = retry
        self.retry_messgae = retry_messgae
        self.sleep = sleep
        self.nb_requests=0

    def translate(self, text, src='auto', dest='en'):

        if src != 'auto':
            if src.lower() in LANGCODES:
                src = LANGCODES[src]
            elif src.lower() in LANGUAGES:
                src = src
            else:
                raise ValueError('invalid source language')

        if dest != 'en':
            if dest.lower() in LANGCODES:
                dest = LANGCODES[src.lower()]
            elif dest.lower() in LANGUAGES:
                dest = dest
            else:
                raise ValueError('invalid destination language')
        to_translate=text
        if not isinstance(to_translate, list):
            to_translate=[to_translate]
        data = self._translate(to_translate, src=src, dest=dest)


        resutlts= self.extract_translation(data, dest)
        if not isinstance(text, list):
            if resutlts:
                return resutlts[0]
            else:
                print(text)
                return None
        return resutlts

    def extract_translation(self, translation_data, target_lang):
        result_list = []
        for _data in translation_data:
            source = _data[1][4][0]
            try:
                translated = utils.format_translation(_data)
            except IndexError:
                translated = [source]
            src='und'
            if len(_data)>2:
                src = _data[2]
            dest = target_lang
            # put final values into a new Translated object
            result = Translated(src=src, origin=source,
                                    text=translated)
            result_list.append(result)
        return result_list

    def parse(self, data: str) -> str:
        matches = re.findall(r"\n\d+\n", data)
        return data[data.index(matches[0]) + len(matches[0]):data.index(matches[1])]

    def run_request(self, text, src, dest):
        try:
            response = requests.post(
                url="https://translate.google.com/_/TranslateWebserverUi/data/batchexecute?" +
                    urlencode({
                        "rpcids": "MkEWBc",
                        "rt": 'c'
                    }),
                headers={
                    "content-type": "application/x-www-form-urlencoded;charset=UTF-8"
                },
                data=urlencode({
                    "f.req": json.dumps(
                        [[[
                            "MkEWBc",
                            str([
                                [
                                    text,
                                    src,
                                    dest,
                                    True
                                ],
                                [None]
                            ]),
                            None,
                            "generic"
                        ]]]
                    )
                }, quote_via=quote)
            )
            return response
        except:
            return None

    def _translate(self, texts, src, dest):
        """ Generate Token for each Translation and post requset to
        google web api translation and return an response

        If the status code is 200 the request is considered as an success
        else other status code are consider as translation failure.

        """

        translated_list = []
        for text in texts:
            response=self.run_request(text, src, dest)
            if response is None:
                continue
            if response.status_code == 200:
                pass
            elif response.status_code == 429:
                _format_data = self.retry_request(text, src, dest)
            else:
                raise Exception('Unexpected status code {} from {}'.format(response.status_code, self.transurl))

            translation_data = json.loads(self.parse(response.text))
            if translation_data[0][2] is not None:
                translated_list.append(json.loads(translation_data[0][2]))
        return translated_list

    def retry_request(self, text, src, dest):
        """ 
        For bulk translation some times translation might failed
        beacuse of too many attempts. for such a case before hitting
        translation api wait for some time and retrying again
        """
        print("retrying")
        retry = self.retry
        sleep = self.sleep

        for i in range(0, retry):
            response = self.run_request(text, src, dest)
            if response is None:
                continue
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                if self.retry_messgae:
                    print('retrying translation after {}s'.format(sleep))
                time.sleep(sleep)
                sleep = i * sleep
            else:
                raise Exception('Unexpected status code {} from {}'.format(response.status_code, self.transurl))

        raise Exception('Unexpected status code {} from {} after retried {} loop with {}s delay'.format(response.status_code, self.transurl, retry, self.sleep))
