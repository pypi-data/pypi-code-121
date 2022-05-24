import math

import pynumparser
from crawlite import BaseCrawler
from crawlite import urlpattern, urlrender


from .extractors import detail
from . import settings



MAX_QUESTION_PAGE = 30
MAX_COMMENT_PAGE = 20
COMMENT_PAGE_COUNT = 100



def parse_page_range_expression(exp):
    if isinstance(exp, str):
        if exp.isnumeric():
            page_range = range(1, int(exp)+1)
        else:
            pnp = pynumparser.NumberSequence(limits=(1,MAX_QUESTION_PAGE))
            page_range = pnp.parse(exp)
    elif isinstance(exp, int):
        page_range = range(1, exp+1)
    elif isinstance(exp, (list, tuple)):
        page_range = exp
    else:
        page_range = range(1, MAX_QUESTION_PAGE)
    return page_range


class NaverKinCrawler(BaseCrawler):
    COMMENT_PAGE_COUNT = 100
    PROXIES_LIST = [
        # None,
        # {'https':'103.37.141.68:80'},
        # {'https':'140.227.61.156:23456'},
        # {'https':'121.254.195.12:8080'},
    ]

    urlorders = [
        urlrender(
            'https://kin.naver.com/search/list.naver',
            urlrenderer='kin_page_urlrenderer',
            # parser='kin_page_parser',
            name='kin_page'
        ),
        urlpattern(
            r'https://kin.naver.com/qna/detail.naver\?d1id=(?P<d1id>\d+)&dirId=(?P<dirId>\d+)&docId=(?P<docId>\d+).+$',
            fields=['d1id', 'dirId', 'docId'],
            parser='kin_detail_parser', extractor=detail,
            name='kin_detail',
        ),
        urlrender(
            urlrenderer='kin_image_urlrenderer',
            parser='kin_image_parser',
            name='kin_image',
        ),
        urlrender(
            'https://kin.naver.com/ajax/detail/commentListAjax.naver',
            urlrenderer='kin_comment_urlrenderer',
            parser='kin_comment_parser',
            name='kin_comment'
        )
    ]


    def __init__(self, keywords, page_range, **kwargs):
        super().__init__(**kwargs)
        self.keywords = keywords
        self.page_range = parse_page_range_expression(page_range)

    def _generate_slug(self, meta, *args):
        m = meta.match
        return '-'.join([
            f"{arg}:{m(arg)}" for arg in args
        ])
    
    def _resolve_slug(self, slug):
        slugset = {}
        for keyval in slug.split('-'):
            key, val = keyval.split(':')
            slugset[key] = val
        return slugset

    
    def kin_page_urlrenderer(self):
        for npage in self.page_range:
            yield dict(
                page=npage,
                query=self.keywords
            )


    def kin_detail_parser(self, response, parsed, meta):
        # print('kin_detal_parser')
        question = dict(
            title = parsed['question_title'],
            url=response.url
        )
        _content_id = {
            key:meta.query[key] for key in 
            ['d1id', 'dirId', 'docId']
        }

        question_content_question = dict(
            question=question,
            type="question",
            url=f"{response.url}#0",
            content = parsed['question_content'],
            kinuser = {
                'username': parsed['question_author'],
                'uid': '',
            },
            pub_date=parsed['question_date'],
            _comment_count=parsed['question_comment_count'],
            _img_srcs=parsed['question_images'],
            _content_id={
                'answerNo': 0,
                **_content_id
            }
        )
        question_content_answers = [
            dict(
                question=question,
                type="answer",
                url=f"{response.url}#{answer['answer_no']}",
                content=answer['answer_content'],
                user = {
                    'username': answer['author_name'],
                    'uid': answer['author_uid'],
                },
                pub_date = answer['answer_date'],
                _img_srcs=answer['answer_images'],
                _comment_count=answer['answer_comment_count'],
                _content_id={
                    'answerNo': answer['answer_no'],
                    **_content_id
                }

            )
            for answer in parsed['answer']
        ]
        self.question_contents = [question_content_question, *question_content_answers]
        return self.question_contents

    
    def kin_image_urlrenderer(self):
        for content in self.question_contents:
            self.content = content
            yield from content['_img_srcs']

    def kin_image_parser(self, response):
        img = dict(
            question_content=self.content,
            src=response.url,
            image=response.content
        )
        yield img


    def kin_comment_urlrenderer(self):
        for content in self.question_contents:
            last_page_number = math.ceil(content['_comment_count']/self.COMMENT_PAGE_COUNT)
            self.content = content
            for npage in range(1, last_page_number+1):
                yield dict(
                    page=npage,
                    count=self.COMMENT_PAGE_COUNT,
                    **content['_content_id']
                )
    
    def kin_comment_parser(self, response):
        parsed = response.json()
        comment_list = parsed['result']['commentList']
        for comment in comment_list:
            yield dict(
                question_content=self.content['url'],
                url=f"{response.url}#{comment['commentNo']}",
                content=comment['contents'],
                wroted = comment['writeTime'],
                user = {
                    'username': comment['viewId'],
                    'uid': comment['u']
                }
            )
    
    def default_breaker(self, response):
        return False
    
    def default_suspender(self, response, suspended, context):
        print('suspended:', suspended)
        return 10
        


def event_listener(module, event, count):
    print(module, event, count)
    return True

def test_naverkin(keywords, page_range):
    nkc = NaverKinCrawler(keywords, page_range,
        settings=settings,
        # crawl_listener=event_listener
    )
    nkc.crawl()
    return nkc
