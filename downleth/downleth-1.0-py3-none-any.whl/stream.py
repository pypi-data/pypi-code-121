import aiohttp
import m3u8
import random
import asyncio
from dataclasses import dataclass
from downleth.common import HEADERS, PurgedSet


CACHE_BUST = random.randint(10 ** 9, 10 ** 10)
SERVER = random.randint(1, 2)
INDEX_TEMPLATE = 'https://oc-vp-livestreaming0{0}.ethz.ch/hls/{1}/index.m3u8?cache={2}'
PURGED_SET_SIZE = 100

def get_index_url(room_id: str):
    return INDEX_TEMPLATE.format(SERVER, room_id, CACHE_BUST)

async def get_index(room_id: str) -> m3u8.M3U8:
    url = get_index_url(room_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS, verify_ssl=True) as response:
            text = await response.text()
            res = m3u8.M3U8(text, base_uri=str(response.url))
            return res

@dataclass
class StreamSegment:
    seg_id: int
    url: str

# generates segments asynchronously, a segment is guaranteed to be returned only once
# however, the segments are not guaranteed to arrive in order, this allows a consumer
# to avoid issues similar to TCP head-of-line blocking
async def generate_segments(room_id: str):
    index = await get_index(room_id)
    wait_time = index.target_duration
    purged_set = PurgedSet(PURGED_SET_SIZE)
    while True:
        for segment in index.segments:
            seg_id = int(segment.uri[:-len('.ts')])
            if not purged_set.has_recently_seen(seg_id):
                yield StreamSegment(seg_id=seg_id, url=segment.absolute_uri)
                purged_set.mark(seg_id)

        [_, index] = await asyncio.gather(
            asyncio.sleep(wait_time),
            get_index(room_id)
        )
