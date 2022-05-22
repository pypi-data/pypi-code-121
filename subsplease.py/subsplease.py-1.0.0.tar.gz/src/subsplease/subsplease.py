from typing import List
import aiohttp
import async_timeout
import feedparser

from .release import Release

class SubsPlease:
    def __init__(self) -> None:
        self._torrent_url = "https://subsplease.org/rss/?t"
        self._magnet_url = "https://subsplease.org/rss/"

    async def _get(self, rss_url):
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(10):
                async with session.get(rss_url) as response:
                    return await response.text()
    
    async def get_latest_torrent(self) -> List[Release]:
        feed = await self._get(self._torrent_url)

        rss = feedparser.parse(feed)
        entries = rss["entries"]
        releases: List[Release] = []

        for entry in entries:
            releases.append(
                Release(
                    title=entry["title"],
                    link=entry["link"],
                    guid=entry["id"],
                    tags=entry["tags"],
                    size=entry["subsplease_size"],
                    release_date=entry["published"],
                    raw=entry,
                )
            )
        return releases

    async def get_latest_magnet(self) -> List[Release]:
        feed = await self._get(self._magnet_url)

        rss = feedparser.parse(feed)
        entries = rss["entries"]
        releases: List[Release] = []

        for entry in entries:
            releases.append(
                Release(
                    title=entry["title"],
                    link=entry["link"],
                    guid=entry["id"],
                    tags=entry["tags"],
                    size=entry["subsplease_size"],
                    release_date=entry["published"],
                    raw=entry,
                )
            )
        return releases