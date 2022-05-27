import inspect
from collections import abc
from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime, date

from crawlite.utils.regex import strcompile
from crawlite.utils.module import FromSettingsMixin

from .exceptions import *


class SoupParser(FromSettingsMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _load_soup(self, content):
        soup = self.apply_settings(BeautifulSoup, content, setting_prefix='BS4_')
        return soup

    def _is_parsable(self, response):
        content_type_info = response.headers.get('Content-Type')
        if not content_type_info:
            return False

        for ctype in self.PARSE_CONTENT_TYPES:
            if ctype in content_type_info:
                return True
        return False
    
    def parse_linkpattern(self, content, urlpattern, remove_duplicates=True, attrs=None, css_selector=None, **kwargs):
        soup = self._load_soup(content)
        if css_selector:
            soup = soup.select_one(css_selector) or soup

        compiled = strcompile(urlpattern)

        parsed = [
            sp[attr]
            for attr in attrs or self.CRAWL_TARGET_ATTRS
            for sp in soup(attrs={attr: compiled})
        ]

        if remove_duplicates:
            parsed = list(dict.fromkeys(parsed))
        return parsed
    
    def validate_extracted(self, extracted, func, meta):
        if extracted is None:
            raise ExtractorReturnNoneValue(f'{func.__name__} cannot return type None')
        
        if not isinstance(meta.soup, BeautifulSoup):
            raise CannotExtractError(f"{func.__name__} won't recive soup instance or None")
 
        if isinstance(extracted, Tag):
            if self.EXTRACT_AUTO_SOUP2TEXT:
                extracted = extracted.get_text(strip=self.EXTRACT_AUTO_STRIP)

        elif isinstance(extracted, str):
            if self.EXTRACT_AUTO_STRIP:
                extracted = extracted.strip()
        elif isinstance(extracted, (int, float)):
            return extracted
        elif isinstance(extracted, (datetime, date)):
            return extracted
        elif isinstance(extracted, (list, tuple, map, filter)) or inspect.isgenerator(extracted):
            extracted_list = [
                self.validate_extracted(ext, func, meta) for ext in extracted
            ]
            return extracted_list
        elif isinstance(extracted, abc.Mapping):
            for key, val in extracted.items():
                extracted[key] = self.validate_extracted(val, func, meta)
            return extracted
        else:
            raise ValueError(
                f"{func.__name__} must return type of str, list, tuple, mapping, generator, date(time), or BeautifulSoup Element Tag instance"
                f"Not f{type(extracted)}"
            )

        return extracted
        

        



    

    

