import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from .downloader import Downloader
from ..extractor.htmlextractor import HtmlExtractor, DynamicHtmlExtractor
from ..series.gogo_series import SeriesUrlGenerator

GOGO_URL = 'https://gogoplay5.com/videos'


class DownloadLink:
    def __init__(self, _id: int, series_name: str, episode: int, download_links: str):
        self.id = _id
        self.series_name = series_name
        self.episode = episode
        self.download_links = download_links

    def __repr__(self):
        return "id: {0}, series_name: {1}, episode {2}, download_links: {3}".format(
            self.id, self.series_name, str(self.episode), self.download_links)


class GogoDownload:

    def __init__(self):
        self.series_generator = SeriesUrlGenerator(GOGO_URL)
        self.downloader = Downloader()

    def extract_episode_urls(self, series_name):
        return self.series_generator.find_episode_urls(series_name)

    def extract_episode_download_url(self, episode_url):
        # if (series_name, episode) in self.cache and cache:
        #    return DownloadLink(0, series_name, episode, self.cache[(series_name, episode)])
        html_extractor = HtmlExtractor(episode_url)
        url = html_extractor.extract_iframe_src()
        if url[:6] != 'https:':
            download_url = 'https:' + url
        else:
            download_url = url
        return download_url.replace('streaming.php?', 'download?')

    def extract_episode_download_link_object(self, series_name, episode, request: DynamicHtmlExtractor.Request):
        download_url = request.url
        dynamic_extractor = DynamicHtmlExtractor(download_url)
        res = dynamic_extractor.extract_download_div_class(request)
        if not res:
            raise Exception("Could not load dynamic content at url: {0} ".format(download_url))
        download_link_obj = DownloadLink(0, series_name, episode, json.dumps(res))
        return download_link_obj

    def download(self, series_name, episode, location, request: Downloader.Request):
        return self.downloader.download(series_name=series_name, episode=episode, location=location, request=request)

    def extract_series_download_url(self, series_name):
        response = []
        for i, ep_url in enumerate(self.series_generator.find_episode_urls(series_name)):
            html_extractor = HtmlExtractor(ep_url)
            url = html_extractor.extract_iframe_src()
            if url[:6] != 'https:':
                download_url = 'https:' + url
            else:
                download_url = url
            download_url = download_url.replace('streaming.php?', 'download?')
            dynamic_extractor = DynamicHtmlExtractor(download_url)
            res = dynamic_extractor.extract_download_div_class()
            download_link_obj = DownloadLink(0, series_name, i + 1, json.dumps(res))

            response.append(download_link_obj)

        return response
