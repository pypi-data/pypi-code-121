import os
import sys
from datetime import datetime, timezone
from logging import Logger, getLogger
from configparser import ConfigParser

log: Logger = getLogger(__name__)


class Page:
    def __init__(self,
                 name: str,
                 ctime: float,
                 mtime: float,
                 html: str,
                 meta: dict,
                 config: ConfigParser):
        log.debug('initializing the page object with name "%s"', name)
        # initial data
        self.name: str = name
        self.ctimestamp: float = ctime
        self.mtimestamp: float = mtime
        self.content: str = html
        self.meta: dict = meta
        self.config: ConfigParser = config

        # data from self.meta
        self.title: str = ''
        self.author: str = ''
        self.cdatetime: datetime = None
        self.mdatetime: datetime = None
        self.summary: str = ''
        self.lang: str = 'en'
        self.tags: list[tuple[str]] = []

        # constructed
        self.url: str = ''
        self.image_url: str = ''
        self.cdate: str = ''
        self.cdate_list: str = ''
        self.cdate_list_sep: str = ''
        self.cdate_rss: str = ''
        self.cdate_sitemap: str = ''
        self.mdate: str = None
        self.mdate_list: str = None
        self.mdate_list_sep: str = None
        self.mdate_rss: str = ''
        self.mdate_sitemap: str = ''

        # later assigned references to next and previous pages
        self.next: Page = None
        self.previous: Page = None

        # also from self.meta, but for og metadata
        self.og: dict[str, str] = dict()


    def __lt__(self, other):
        return self.ctimestamp < other.ctimestamp


    def __get_mandatory_meta(self, meta: str) -> str:
        try:
            log.debug('parsing required metadata "%s"', meta)
            return self.meta[meta][0]
        except KeyError:
            log.error('failed to parse mandatory metadata "%s" from file "%s"',
                      meta, os.path.join(self.config.get('path', 'src'), self.name))
            sys.exit(1)


    # parses meta from self.meta, for og, it prioritizes,
    # the actual og meta
    def parse_metadata(self):
        log.debug('parsing metadata for file "%s"', self.name)
        self.title = self.__get_mandatory_meta('title')
        self.author = self.__get_mandatory_meta('author')
        self.summary = self.__get_mandatory_meta('summary')
        self.lang = self.__get_mandatory_meta('lang')

        log.debug('parsing timestamp')
        self.cdatetime = datetime.fromtimestamp(self.ctimestamp,
                                                 tz=timezone.utc)
        self.cdate = self.cdatetime.strftime(self.config.get('fmt', 'date'))
        self.cdate_list = self.cdatetime.strftime(self.config.get('fmt', 'list_date'))
        self.cdate_list_sep = self.cdatetime.strftime(self.config.get('fmt', 'list_sep_date'))
        self.cdate_rss = self.cdatetime.strftime(self.config.get('fmt', 'rss_date'))
        self.cdate_sitemap = \
        self.cdatetime.strftime(self.config.get('fmt', 'sitemap_date'))

        if self.mtimestamp != 0.0:
            log.debug('parsing modified timestamp')
            self.mdatetime = datetime.fromtimestamp(self.mtimestamp,
                                                     tz=timezone.utc)
            self.mdate = self.mdatetime.strftime(self.config.get('fmt', 'date'))
            self.mdate_list = self.mdatetime.strftime(self.config.get('fmt', 'list_date'))
            self.mdate_list_sep = self.mdatetime.strftime(self.config.get('fmt', 'list_sep_date'))
            self.mdate_rss = self.mdatetime.strftime(self.config.get('fmt', 'rss_date'))
            self.mdate_sitemap = \
            self.mdatetime.strftime(self.config.get('fmt', 'sitemap_date'))
        else:
            log.debug('not parsing modified timestamp, hasn\'t been modified')

        try:
            tags_only: list[str] = self.meta['tags']
            log.debug('parsing tags')
            tags_only.sort()

            for t in tags_only:
                self.tags.append((t,
                                  f'{self.config.get("url", "main")}/tag/@{t}.html'))
        except KeyError:
            log.debug('not parsing tags, doesn\'t have any')

        log.debug('parsing url')
        self.url = f'{self.config.get("url", "main")}/{self.name.replace(".md", ".html")}'
        log.debug('final url "%s"', self.url)

        log.debug('parsing image url')
        try:
            self.image_url = \
            f'{self.config.get("url", "static")}/{self.meta["image_url"][0]}'
        except KeyError:
            log.debug('using default image, no image_url metadata found')
            self.image_url = \
            f'{self.config.get("url", "static")}/{self.config.get("url", "default_image")}'
        log.debug('final image url "%s"', self.image_url)

        # if contains open graph elements
        try:
            # og_e = object graph entry
            og_elements: list[str] = self.meta['og']
            log.debug('parsing og metadata')
            for og_e in og_elements:
                kv: str = og_e.split(',', 1)
                if len(kv) != 2:
                    log.error('invalid og syntax for "%s", needs to be "k, v"', og_e)
                    sys.exit(1)

                k: str = kv[0].strip()
                v: str = kv[1].strip()

                log.debug('og element: ("%s", "%s")', k, v)
                self.og[k] = v
        except KeyError:
            log.debug('no og metadata found')
