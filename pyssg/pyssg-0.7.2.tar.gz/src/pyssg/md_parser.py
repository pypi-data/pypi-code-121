import os
from operator import itemgetter
from markdown import Markdown
from configparser import ConfigParser
from logging import Logger, getLogger

from markdown import Markdown
from yafg import YafgExtension
from MarkdownHighlight.highlight import HighlightExtension
from markdown_checklist.extension import ChecklistExtension

from .database import Database
from .page import Page

log: Logger = getLogger(__name__)


def _get_md_obj() -> Markdown:
    exts: list = ['extra',
                  'meta',
                  'sane_lists',
                  'smarty',
                  'toc',
                  'wikilinks',
                  # stripTitle generates an error when True,
                  # if there is no title attr
                  YafgExtension(stripTitle=False,
                                figureClass="",
                                figcaptionClass="",
                                figureNumbering=False,
                                figureNumberClass="number",
                                figureNumberText="Figure"),
                  HighlightExtension(),
                  ChecklistExtension(),
                  'pymdownx.caret',
                  'pymdownx.tilde']
    log.debug('list of md extensions: (%s)',
              ', '.join([e if isinstance(e, str) else type(e).__name__
                         for e in exts]))
    return Markdown(extensions=exts, output_format='html5')


# page and file is basically a synonym here...
class MDParser:
    def __init__(self, files: list[str],
                 config: ConfigParser,
                 db: Database):
        log.debug('initializing the md parser with %d files', len(files))
        self.files: list[str] = files

        self.config: ConfigParser = config
        self.db: Database = db
        self.md: Markdown = _get_md_obj()

        self.all_files: list[Page] = None
        # updated and modified are synonyms here
        self.updated_files: list[Page] = None
        self.all_tags: list[tuple[str]] = None


    def parse_files(self) -> None:
        log.debug('parsing all files')
        # initialize lists
        self.all_files = []
        self.updated_files = []
        self.all_tags = []
        # not used, not sure why i had this
        # all_tag_names: list[str] = []

        for f in self.files:
            log.debug('parsing file "%s"', f)
            src_file: str = os.path.join(self.config.get('path', 'src'), f)
            log.debug('path "%s"', src_file)
            # get flag if update is successful
            file_updated: bool = self.db.update(src_file, remove=f'{self.config.get("path", "src")}/')

            log.debug('parsing md into html')
            content: str = self.md.reset().convert(open(src_file).read())
            page: Page = Page(f,
                              self.db.e[f][0],
                              self.db.e[f][1],
                              content,
                              self.md.Meta,
                              self.config)
            page.parse_metadata()

            # keep a separated list for all and updated pages
            if file_updated:
                log.debug('has been modified, adding to mod file list')
                self.updated_files.append(page)
            log.debug('adding to file list')
            self.all_files.append(page)

            # parse tags
            if page.tags is not None:
                log.debug('parsing tags')
                # add its tag to corresponding db entry if existent
                self.db.update_tags(f, list(map(itemgetter(0), page.tags)))

                log.debug('add all tags to tag list')
                for t in page.tags:
                    if t[0] not in list(map(itemgetter(0), self.all_tags)):
                        log.debug('adding tag "%s" as it\'s not present in tag list', t[0])
                        self.all_tags.append(t)
                    else:
                        log.debug('ignoring tag "%s" as it\'s present in tag list', t[0])
            else:
                log.debug('no tags to parse')

        log.debug('sorting all lists for consistency')
        self.all_tags.sort(key=itemgetter(0))
        self.updated_files.sort(reverse=True)
        self.all_files.sort(reverse=True)

        pages_amount: int = len(self.all_files)
        # note that prev and next are switched because of the
        # reverse ordering of all_pages
        log.debug('update next and prev attributes')
        for i, p in enumerate(self.all_files):
            if i != 0:
                next_page: Page = self.all_files[i - 1]
                p.next = next_page

            if i != pages_amount - 1:
                prev_page: Page = self.all_files[i + 1]
                p.previous = prev_page
