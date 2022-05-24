from itertools import count
from crawlite import BaseCrawler, urlrender
from crawlite.utils.urls import urljoin

from .extractors import place_detail
from .payloaders import gen_review_request_payloader
from .utils import str2date


COUNT_PER_PAGE = 100

config = {
    'REQUEST_CACHE_BACKEND': 'sqlite',
    # 'REQUEST_CACHE_BACKEND': 'memory',
    'REQUEST_DELAY': (1, 1.5),
    'REQUESTS_TIMEOUT': 5,
    'REQUEST_CACHE_CACHE_NAME': 'naverplace.sqlite'

}


class NaverPlaceCrawler(BaseCrawler):
    HEADERS = {
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    }

    urlorders = [
        urlrender(
            'https://map.naver.com/v5/api/instantSearch', fields=['coords', 'query'], 
            urlrenderer='naverplace_search_urlrenderer',
            parser='naverplace_search_parser',
            name='naverplace_search', refresh=True
        ),
        urlrender('https://pcmap.place.naver.com/restaurant/',
            urlrenderer='naverplace_detail_urlrenderer',
            parser='naverplace_detail_parser', extractor=place_detail,
            name='naverplace_detail'
        ),
        urlrender(
            'https://pcmap-api.place.naver.com/graphql',
            payloader='naverplace_review_payloader',
            parser='naverplace_review_parser', name='naverplace_review'
        ),
    ]

    def __init__(self, keyword, visited=None, **kwargs):
        super().__init__(settings=config, **kwargs)
        self.keyword = keyword
        self.visited = visited or set()
        self.tmp_place = None
        self.end_page = 1
        self._is_break = False
        self.count = 0

    def naverplace_search_urlrenderer(self):
        yield {'coords': '37.52725,126.9682994', 'query': self.keyword}
    
    def naverplace_search_parser(self, response):
        for place in response.json().get('place', []):
            record = dict(
                place_id=place['id'],
                place_name=place['title'],
                road_address=place['roadAddress']
            )
            self.tmp_place = record
            break
    
    def naverplace_detail_urlrenderer(self, url):
        if self.tmp_place:
            place_id = self.tmp_place['place_id']
            yield urljoin(url, place_id)
    

    def naverplace_detail_parser(self, parsed):
        yield dict(**self.tmp_place, **parsed)
    
    def naverplace_review_payloader(self):
        page = 1
        place_id = self.tmp_place['place_id']
        while page <= self.end_page:
            if self._is_break:
                break
            yield gen_review_request_payloader(place_id, page, COUNT_PER_PAGE)
            page += 1


    def naverplace_review_parser(self, response):
        place_id = self.tmp_place['place_id']
        if data:= response.json():
            data = data[0]['data']
            self.end_page = data['visitorReviews']['total'] // COUNT_PER_PAGE + 1
            reviews = data['visitorReviews']
            items = reviews['items']
            for row in items:
                review_id=row['id']
                if review_id in self.visited:
                    self._is_break = True
                    continue
                record = dict(
                    review_id=review_id,
                    place=place_id,
                    author_name = row['author']['nickname'],
                    author_id = row['author']['id'],
                    content = row['body'],
                    visit_count = row['visitCount'],
                    visited = str2date(row['visited']),
                    published = str2date(row['created']),
                    tags=[
                        t['displayName'] for t in row['votedKeywords']
                    ]
                )
                self.count += 1
                yield record







    
def crawl_naver_place(place_name):
    npc = NaverPlaceCrawler(place_name)
    npc.crawl()
    return npc.results