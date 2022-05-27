__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import urllib.error
import urllib.request
from io import BytesIO

from lxml import etree

from media_tools.util.buying.retry_http import retry_http
from media_tools.util.buying.track import Track


class Distributor:

    def search_url(self, track: Track) -> str:
        raise NotImplementedError()

    def is_present(self, track: Track) -> bool:
        raise NotImplementedError()


class Beatport(Distributor):

    def search_url(self, track: Track) -> str:
        return f'http://www.beatport.com/search?q="{track.artist}"+"{track.title}"'

    @retry_http()
    def is_present(self, track: Track) -> bool:
        with urllib.request.urlopen(self.search_url(track)) as response:
            html = etree.parse(BytesIO(response.read()), etree.HTMLParser())
            if html.xpath('//ul[@class ="bucket-items"]'):
                return True
            return bool(html.xpath('//h2[contains(., "Tracks")]'))


class Amazon(Distributor):

    def search_url(self, track: Track) -> str:
        return 'https://smile.amazon.de/s/ref=nb_sb_noss?url=search-alias%3Daps&' \
               f'field-keywords="{track.artist}"+"{track.title}"'

    @retry_http()
    def is_present(self, track: Track) -> bool:
        with urllib.request.urlopen(self.search_url(track)) as response:
            html = etree.parse(BytesIO(response.read()), etree.HTMLParser())
            return bool(html.xpath("//ul[@id='s-results-list-atf']"))
