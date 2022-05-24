from requests import get
from exceptions import *


class Client:
    def __init__(self):
        self.endpoints = {
            'ideas': 'https://artilities.herokuapp.com/api/ideas',
            'challenges': 'https://artilities.herokuapp.com/api/challenges',
            'dictionary': 'https://artilities.herokuapp.com/api/dict?',
            'patrons': 'https://artilities.herokuapp.com/api/other/patrons',
            'banners': 'https://artilities.herokuapp.com/api/other/banners'
        }
        self.cached_ideas = list(),
        self.cached_challenges = list(),
        self.cached_queries = list()

    def append_att(self, att_name, element):
        try:
            self.__dict__[att_name][0].append(element)
        except:
            self.__dict__[att_name].append(element)

    def generate_idea(self):
        response = get(self.endpoints['ideas'])
        if response.json()['status_code'] == 200:
            self.append_att('cached_ideas', response)
            return response
        else:
            raise errorResponse(response.json()['error_response'])

    def generate_challenge(self):
        response = get(self.endpoints['challenges'])
        if response.json()['status_code'] == 200:
            self.append_att('cached_challenges', response)
            return response
        else:
            raise errorResponse(response.json()['error_response'])

    def get_patrons(self):
        response = get(self.endpoints['patrons'])
        if response.json()['status_code'] == 200:
            return response
        else:
            raise errorResponse(response.json()['error_response'])

    def get_banner(self):
        response = get(self.endpoints['banners'])
        if response.json()['status_code'] == 200:
            return response
        else:
            raise errorResponse(response.json()['error_response'])

    def dict_query(self, query: str = None, lang: str = None):
        if query is not None:
            if lang in [None, 'eng', 'ru']:
                response = get(
                    self.endpoints['dictionary'] + f"query={query}" + (f'&lang={lang}' if lang is not None else '')
                )
                print(response.json())
                if len(response.json()['query_results']) > 0:
                    self.append_att('cached_queries', (response, 'eng' if lang is None else lang))
                    return response
                else:
                    raise dictNotFound
            else:
                raise dictLangParameterIncorrect
        else:
            raise dictQueryIncomplete
