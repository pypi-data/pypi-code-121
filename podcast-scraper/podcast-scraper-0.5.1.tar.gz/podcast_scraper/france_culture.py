import datetime
import logging
from html import unescape

import requests
from podcast_scraper.api_scraper import ApiScraper


class FranceCulture(ApiScraper):
    current_cursor = ""
    URL_FIRST = "https://www.radiofrance.fr/api/v1.7/path?value=franceculture/podcasts/{emission}"
    URL = "https://www.radiofrance.fr/api/v1.7/concepts/{concept}/expressions?pageCursor={current_cursor}&includeFutureExpressionsWithManifestations=true"

    def __init__(self, emission):
        self.emission = emission.split("/")[-1]

    def get_url(self):
        if self.page_count == 0:
            return self.URL_FIRST.format(emission=self.emission)
        return self.URL.format(concept=self.concept, current_cursor=self.current_cursor)

    def get_objects(self):
        data = requests.get(self.get_url())
        if data.status_code != 200:
            logging.error("Unexpected erro fetching the result", data)
        if self.page_count == 0:
            content = data.json()["content"]
            self.concept = content["id"]
            self.title = content["title"]
            expressions = content["expressions"]
            items = expressions["items"]
            current_cursor = expressions["next"]
        else:
            content = data.json()
            items = content["items"]
            current_cursor = content["next"]
        return (items, current_cursor)

    def get_content(self):
        if self.current_cursor is None:
            return None

        urls = []
        titles = []
        albums = []
        dates = []
        (items, current_cursor) = self.get_objects()
        for item in items:
            title = (
                item["episodeSerieTitle"]
                if "episodeSerieTitle" in item
                else item["title"]
            )
            titles.append(title)
            dates.append(
                str(datetime.datetime.fromtimestamp(item["publishedDate"]).year)
            )
            manifestations = item["manifestations"]
            if len(manifestations):
                urls.append(manifestations[0]["url"])
            else:
                urls.append(None)

        self.current_cursor = current_cursor
        result = {
            "artist": [unescape(self.title)] * len(titles),
            "album": [unescape(self.title)] * len(titles),
            "title": titles,
            "date": dates,
            "file": [None if url is None else url.split("/")[-1] for url in urls],
            "url": urls,
        }
        return result
