import os
from copy import deepcopy
from operator import itemgetter
from configparser import ConfigParser
from logging import Logger, getLogger

from jinja2 import Environment, Template, FileSystemLoader as FSLoader

from .utils import get_file_list, get_dir_structure, create_dir, copy_file
from .database import Database
from .md_parser import MDParser
from .page import Page

log: Logger = getLogger(__name__)


class Builder:
    def __init__(self, config: ConfigParser,
                 db: Database):
        log.debug('initializing site builder')
        self.config: ConfigParser = config
        self.db: Database = db

        # the autoescape option could be a security risk if used in a dynamic
        # website, as far as i can tell
        log.debug('initializing the jinja environment')
        self.__loader: FSLoader = FSLoader(self.config.get('path', 'plt'))
        self.env: Environment = Environment(loader=self.__loader,
                                            autoescape=False,
                                            trim_blocks=True,
                                            lstrip_blocks=True)

        self.dirs: list[str] = None
        self.md_files: list[str] = None
        self.html_files: list[str] = None

        # files and pages are synoyms
        self.all_files: list[Page] = None
        self.updated_files: list[Page] = None
        self.all_tags: list[str] = None
        self.common_vars: dict = None


    def build(self) -> None:
        log.debug('building site')
        self.dirs = get_dir_structure(self.config.get('path', 'src'),
                                      ['templates'])
        self.md_files = get_file_list(self.config.get('path', 'src'),
                                      ['.md'],
                                      ['templates'])
        self.html_files = get_file_list(self.config.get('path', 'src'),
                                        ['.html'],
                                        ['templates'])

        self.__create_dir_structure()
        self.__copy_html_files()

        parser: MDParser = MDParser(self.md_files,
                                    self.config,
                                    self.db)
        parser.parse_files()

        # just so i don't have to pass these vars to all the functions
        self.all_files = parser.all_files
        self.updated_files = parser.updated_files
        self.all_tags = parser.all_tags

        # dict for the keyword args to pass to the template renderer
        log.debug('adding config, all_pages and all_tags to exposed vars for jinja')
        self.common_vars = dict(config=self.config,
                                all_pages=self.all_files,
                                all_tags=self.all_tags)

        self.__render_articles()
        self.__render_tags()
        self.__render_template('index.html', 'index.html', **self.common_vars)
        self.__render_template('rss.xml', 'rss.xml', **self.common_vars)
        self.__render_template('sitemap.xml', 'sitemap.xml', **self.common_vars)


    def __create_dir_structure(self) -> None:
        log.debug('creating dir structure')
        dir_path: str = None
        for d in self.dirs:
            dir_path = os.path.join(self.config.get('path', 'dst'), d)
            # using silent=True to not print the info create dir msgs for this
            create_dir(dir_path, True, True)


    def __copy_html_files(self) -> None:
        if len(self.html_files) > 0:
            log.debug('copying all html files')
        else:
            log.debug('no html files to copy')
        src_file: str = None
        dst_file: str = None

        for f in self.html_files:
            src_file = os.path.join(self.config.get('path', 'src'), f)
            dst_file = os.path.join(self.config.get('path', 'dst'), f)

            # only copy files if they have been modified (or are new)
            if self.db.update(src_file, remove=f'{self.config.get("path", "src")}/'):
                log.debug('file "%s" has been modified or is new, copying', f)
                copy_file(src_file, dst_file)
            else:
                if self.config.getboolean('other', 'force'):
                    log.debug('file "%s" hasn\'t been modified, but option force is set to true, copying anyways', f)
                    copy_file(src_file, dst_file)
                else:
                    log.debug('file "%s" hasn\'t been modified, ignoring', f)


    def __render_articles(self) -> None:
        log.debug('rendering html')
        article_vars: dict = deepcopy(self.common_vars)
        temp_files: list[Page] = None

        # check if only updated should be created
        if self.config.getboolean('other', 'force'):
            log.debug('all html will be rendered, force is set to true')
            temp_files = self.all_files
        else:
            log.debug('only updated or new html will be rendered')
            temp_files = self.updated_files

        for p in temp_files:
            log.debug('adding page to exposed vars for jinja')
            article_vars['page'] = p
            # actually render article
            self.__render_template("page.html",
                                   p.name.replace('.md','.html'),
                                   **article_vars)


    def __render_tags(self) -> None:
        log.debug('rendering tags')
        tag_vars: dict = deepcopy(self.common_vars)
        tag_pages: list[Page] = None
        for t in self.all_tags:
            log.debug('rendering tag "%s"', t[0])
            # clean tag_pages
            tag_pages = []
            log.debug('adding all pages that contain current tag')
            for p in self.all_files:
                if p.tags is not None and t[0] in list(map(itemgetter(0),
                                                           p.tags)):
                    log.debug('adding page "%s" as it contains tag "%s"',
                              p.name, t[0])
                    tag_pages.append(p)

            log.debug('adding tag and tag_pages to exposed vars for jinja')
            tag_vars['tag'] = t
            tag_vars['tag_pages'] = tag_pages

            # actually render tag page
            self.__render_template('tag.html',
                                   f'tag/@{t[0]}.html',
                                   **tag_vars)


    def __render_template(self, template_name: str,
                          file_name: str,
                          **template_vars) -> None:
        log.debug('rendering html "%s" with template "%s"',
                  file_name, template_name)
        template: Template = self.env.get_template(template_name)
        content: str = template.render(**template_vars)
        dst_path: str = os.path.join(self.config.get('path', 'dst'), file_name)

        log.debug('writing html file to path "%s"', dst_path)
        with open(dst_path, 'w') as f:
            f.write(content)
