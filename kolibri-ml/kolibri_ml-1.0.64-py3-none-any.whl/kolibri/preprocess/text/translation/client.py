# -*- coding: utf-8 -*-
"""
A Translation module.

You can translate_ text using this module.
"""
import random
import typing
import time, math
import httpcore
import httpx
import requests
from httpx import Timeout
import re

from kolibri.preprocess.text.translation import utils
from kolibri.preprocess.text.translation.constants import (
    LANGCODES, LANGUAGES, SPECIAL_CASES, GOOGLE_DEFAULT_SERVICE_URLS,
    DEFAULT_RAISE_EXCEPTION, DUMMY_DATA
)
from kolibri.preprocess.text.translation.models import Translated, Detected

from kolibri.logger import get_logger

logger = get_logger(__name__)

EXCLUDES = ('en', 'ca', 'fr')

TRANSLATE = 'https://{host}/translate_a/single'


class Translator:
    """Google Translate ajax API implementation class

    You have to create an instance of Translator to use this API

    :param service_urls: google translate_ url list. URLs will be used randomly.
                         For example ``['translate_.google.com', 'translate_.google.co.kr']``
    :type service_urls: a sequence of strings

    :param user_agent: the User-Agent header to send when making requests.
    :type user_agent: :class:`str`

    :param proxies: proxies configuration.
                    Dictionary mapping protocol or protocol and host to the URL of the proxy
                    For example ``{'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}``
    :type proxies: dictionary

    :param timeout: Definition of timeout for httpx library.
                    Will be used for every request.
    :type timeout: number or a double of numbers
    :param proxies: proxies configuration.
                    Dictionary mapping protocol or protocol and host to the URL of the proxy
                    For example ``{'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}``
    :param raise_exception: if `True` then raise exception if smth will go wrong
    :type raise_exception: boolean
    """
    _ua = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS data x.y; rv:10.0) Gecko/20100101 Firefox/10.0"
    )

    def __init__(self, raise_exception=DEFAULT_RAISE_EXCEPTION, timeout: Timeout = None,
                 http2=True):

        self.client = httpx.Client(http2=http2)

        self.client.headers.update({
            'User-Agent': self._ua,
        })

        if timeout is not None:
            self.client.timeout = timeout

        self.service_url = "translate.googleapis.com"

        self.service_url = random.choice(GOOGLE_DEFAULT_SERVICE_URLS)
        self.raise_exception = raise_exception
        self._session = requests.session()
        self._session.headers.update({"user-agent": self._ua})
        self.__class__._tkk = ""
        self._re_tkk = re.compile(r"tkk=\'(.+?)\'", re.DOTALL)

    def _calc_token(self, text):

        if (
                not self.__class__._tkk
                or int(self.__class__._tkk.split(".")[0]) < int(time.time() / 3600) - 18000
        ):
            logger.debug("generating new tkk")
            # just calling it to simulate human behaviour (as far as possible)
            self._session.get(
                "https://" + self.service_url + "/translate_a/l?client=t&alpha=true&hl=en&cb=callback"
            )

            r = self._session.get(
                "https://" + self.service_url + "/translate_a/element.js?cb=googleTranslateElementInit"

            )
            self.__class__._tkk = self._re_tkk.search(r.text)[1]

        def xor_rot(a, b):
            size_b = len(b)
            c = 0
            while c < size_b - 2:
                d = b[c + 2]
                d = ord(d[0]) - 87 if "a" <= d else int(d)
                d = (a % 0x100000000) >> d if "+" == b[c + 1] else a << d
                a = a + d & 4294967295 if "+" == b[c] else a ^ d
                c += 3
            return a

        a = []
        for i in text:
            val = ord(i)
            if val < 0x10000:
                a += [val]
            else:
                a += [
                    math.floor((val - 0x10000) / 0x400 + 0xD800),
                    math.floor((val - 0x10000) % 0x400 + 0xDC00),
                ]
        b = self.__class__._tkk if self.__class__._tkk != "0" else ""
        d = b.split(".")
        b = int(d[0]) if len(d) > 1 else 0
        e = []
        g = 0
        size = len(text)
        while g < size:
            l = a[g]
            if l < 128:
                e.append(l)
            else:
                if l < 2048:
                    e.append(l >> 6 | 192)
                else:
                    if (
                            (l & 64512) == 55296
                            and g + 1 < size
                            and a[g + 1] & 64512 == 56320
                    ):
                        g += 1
                        l = 65536 + ((l & 1023) << 10) + (a[g] & 1023)
                        e.append(l >> 18 | 240)
                        e.append(l >> 12 & 63 | 128)
                    else:
                        e.append(l >> 12 | 224)
                    e.append(l >> 6 & 63 | 128)
                e.append(l & 63 | 128)
            g += 1
        a = b
        for i, value in enumerate(e):
            a += value
            a = xor_rot(a, "+-a^+6")
        a = xor_rot(a, "+-3^+b+-f")
        a ^= int(d[1]) if len(d) > 1 else 0
        if a < 0:
            a = (a & 2147483647) + 2147483648
        a %= 1000000
        return "{}.{}".format(a, a ^ b)

    def _translate(self, text, dest, src, override):
        token = self._calc_token(text)
        params = utils.build_params(query=text, src=src, dest=dest,
                                    token=token, override=override)

        url = TRANSLATE.format(host=self.service_url)
        r = self.client.get(url, params=params)

        if r.status_code == 200:
            data = utils.format_json(r.text)
            return data, r

        if self.raise_exception:
            raise Exception('Unexpected status code "{}" from {}'.format(
                r.status_code, self.service_url))

        DUMMY_DATA[0][0][0] = text
        return DUMMY_DATA, r

    def _parse_extra_data(self, data):
        response_parts_name_mapping = {
            0: 'translation',
            1: 'all-translations',
            2: 'original-language',
            5: 'possible-translations',
            6: 'confidence',
            7: 'possible-mistakes',
            8: 'language',
            11: 'synonyms',
            12: 'definitions',
            13: 'examples',
            14: 'see-also',
        }

        extra = {}

        for index, category in response_parts_name_mapping.items():
            extra[category] = data[index] if (
                    index < len(data) and data[index]) else None

        return extra

    def translate(self, text, dest='en', src='auto', **kwargs):
        """Translate text from source language to destination language
        """

        self.service_url=random.choice(GOOGLE_DEFAULT_SERVICE_URLS)
        dest = dest.lower().split('_', 1)[0]
        src = src.lower().split('_', 1)[0]

        if src != 'auto' and src not in LANGUAGES:
            if src in SPECIAL_CASES:
                src = SPECIAL_CASES[src]
            elif src in LANGCODES:
                src = LANGCODES[src]
            else:
                raise ValueError('invalid source language')

        if dest not in LANGUAGES:
            if dest in SPECIAL_CASES:
                dest = SPECIAL_CASES[dest]
            elif dest in LANGCODES:
                dest = LANGCODES[dest]
            else:
                raise ValueError('invalid destination language')

        if isinstance(text, list):
            result = []
            for item in text:
                translated = self.translate(item, dest=dest, src=src, **kwargs)
                result.append(translated)
            return result

        origin = text
        data, response = self._translate(text, dest, src, kwargs)

        # this code will be updated when the format is changed.
        translated = ''.join([d[0] if d[0] else '' for d in data[0]])

        extra_data = self._parse_extra_data(data)

        # actual source language that will be recognized by Google Translator when the
        # src passed is equal to auto.
        try:
            src = data[2]
        except Exception:  # pragma: nocover
            pass

        pron = origin
        try:
            pron = data[0][1][-2]
        except Exception:  # pragma: nocover
            pass

        if pron is None:
            try:
                pron = data[0][1][2]
            except:  # pragma: nocover
                pass

        if dest in EXCLUDES and pron == origin:
            pron = translated

        # put final values into a new Translated object
        result = Translated(src=src, origin=origin,
                            text=translated,
                            extra_data=extra_data,
                            response=response)

        return result

    def detect(self, text, **kwargs):
        """Detect language of the input text

        """
        if isinstance(text, list):
            result = []
            for item in text:
                lang = self.detect(item)
                result.append(lang)
            return result

        data, response = self._translate(text, 'en', 'auto', kwargs)

        # actual source language that will be recognized by Google Translator when the
        # src passed is equal to auto.
        src = ''
        confidence = 0.0
        try:
            if len(data[8][0]) > 1:
                src = data[8][0]
                confidence = data[8][-2]
            else:
                src = ''.join(data[8][0])
                confidence = data[8][-2][0]
        except Exception:  # pragma: nocover
            pass
        result = Detected(lang=src, confidence=confidence, response=response)

        return result