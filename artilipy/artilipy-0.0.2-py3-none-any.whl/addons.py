from client import Client
from exceptions import *


class ClientWithAddOns(Client):
    def __init__(self):
        super().__init__()

    def beautifyIdeaCache(self, lang: str = None):
        if lang is not None and lang in ['eng', 'ru']:
            return list(
                map(lambda idea: idea.json()['generated_idea'][lang], self.__dict__['cached_ideas'][0])
            )
        else:
            raise langNotSpecified

    def beautifyChallengeCache(self, lang: str = None):
        if lang is not None and lang in ['eng', 'ru']:
            return list(
                map(lambda idea: idea.json()['generated_challenge'][lang], self.__dict__['cached_challenges'][0])
            )
        else:
            raise langNotSpecified

    def beautifyDictCache(self, lang: str = None):
        existing_cached_languages = list(map(lambda el: el[1], self.__dict__['cached_queries']))
        if lang in existing_cached_languages:
            if lang in ['eng', 'ru']:
                return list(map(lambda el:
                    list(map(
                        lambda query_el: {'word': query_el[0],
                                          'explanation': query_el[1]},
                        el[0].json()['query_results']
                    )), list(
                    filter(lambda query: query[1] == lang, self.__dict__['cached_queries'])
                )))
            else:
                return list(map(
                    lambda el: {
                        list(map(
                            lambda query_el: {'word': query_el[0],
                                              'explanation': query_el[0]},
                            el[0].json()['query_results']
                        ))
                    }, self.__dict__['cached_queries']
                ))
        else:
            raise langIsNotCached
