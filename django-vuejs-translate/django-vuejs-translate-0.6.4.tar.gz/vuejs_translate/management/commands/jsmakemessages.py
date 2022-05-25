import io
import os
import re
from functools import reduce

from django.conf import settings
from django.utils.jslex import prepare_js_for_gettext
from django.utils.functional import cached_property
from django.utils.translation import templatize
from django.core.management.commands.makemessages import BuildFile
from django.core.management.utils import handle_extensions
from django_jinja.management.commands.makemessages import (
    Command as JinjaMakemessagesCommand
)


LOOKUP_FLAGS = re.MULTILINE | re.IGNORECASE
TAG_REGEX_LOOKUPER = re.compile(r'\/[a-z0-9_-]+\>', LOOKUP_FLAGS)
ES6_STRING_TEMPLATES = re.compile(r'\`(([^\`\\]|(\\(.|\n)))*?)\`', LOOKUP_FLAGS)
PUG_INCLUDES = re.compile(r'^\s*include\s+.+$', re.MULTILINE)
PUG_EXTENDS = re.compile(r'^\s*extends\s+.+$', re.MULTILINE)


def clear_regex_tags(content: str) -> str:
    # Replacing all the closing tags because of django's parces them
    # as a beginning of regexp
    return TAG_REGEX_LOOKUPER.sub('>', content)


def clear_es6(content: str) -> str:
    content = ES6_STRING_TEMPLATES.sub(r'"\1"', content)

    return content


def clear_pug(content: str) -> str:
    content = PUG_INCLUDES.sub('', content)
    content = PUG_EXTENDS.sub('', content)
    return content


def clear_all(content: str) -> str:
    return reduce(lambda acc, x: x(acc), (
        clear_regex_tags,
        clear_es6,
        clear_pug,
    ), content)


class JSBuildFile(BuildFile):
    def __init__(self, command, domain, translatable):
        self.command = command
        self.domain = domain
        self.translatable = translatable

    @cached_property
    def is_js(self):
        filename, ext = os.path.splitext(self.path)

        return ext in self.command.options['jsextensions']

    @cached_property
    def is_templatized(self):
        if self.is_js:
            return self.command.gettext_version < (0, 19, 9)
        else:
            file_ext = os.path.splitext(self.translatable.file)[1]

            return file_ext != '.py'

    def clear_content(self, content: str) -> str:
        return clear_all(content)

    def preprocess(self):
        """
        Preprocess (if necessary) a translatable file before passing it to
        xgettext GNU gettext utility.
        """
        if not self.is_templatized:
            return

        encoding = settings.FILE_CHARSET if self.command.settings_available else 'utf-8'
        path = self.path

        with io.open(path, 'r', encoding=encoding) as fp:
            src_data = fp.read()

        if self.is_js:
            content = prepare_js_for_gettext(self.clear_content(src_data))
        else:
            content = templatize(
                src_data, origin=path[2:],
                # charset=encoding
            )

        with io.open(self.work_path, 'w', encoding='utf-8') as fp:
            fp.write(content)


class Command(JinjaMakemessagesCommand):
    build_file_class = JSBuildFile
    default_xgettext_options = ['--from-code=UTF-8', '--add-comments=Translators']

    @property
    def xgettext_options(self):
        return self.default_xgettext_options + self.collect_keywords()

    def collect_keywords(self):
        return [f'--keyword={key}' for key in self.options['keywords']]

    def add_arguments(self, parser):
        parser.add_argument(
            '--jsextension', '-jse',
            default=[],
            dest='jsextensions',
            action='append',
            help=(
                'The file extension(s) to use to tdetermine whether file is '
                'a Javascript file if the domain is "djangojs"). Separate '
                'multiple extensions with commas, or use -e multiple times.'
            )
        )
        parser.add_argument(
            '--keyword', '-k',
            default=[],
            dest='keywords',
            action='append',
            help=(
                'Additional keywords for `xgettext` command.'
            )
        )

        return super().add_arguments(parser)

    def handle(self, *args, **options):
        self.options = options

        options['jsextensions'] = (
            handle_extensions(options['jsextensions']) or set(['js'])
        )

        return super().handle(*args, **options)
