# -*- coding: utf-8 -*-
#
# update_version: automatically fix version numbers while tagging
#
# Copyright (c) 2015 Marcin Kasperski <Marcin.Kasperski@mekk.waw.pl>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# See README.rst for more details.

"""Let 'hg tag' automatically update version numbers in your code.

Manually maintaining various VERSION variables is both painful and
mistake-prone.  This extension automatically updates those values
whenever you tag a new release.

For example, write in your repository ``.hg/hgrc``::

    [update_version]
    active = true
    language = python
    tagfmt = dotted

and whenever you type::

    hg tag 0.3.7

files like setup.py, __init__.py, and version.py will be scanned for
version variables, and those will be updated to contain ``0.3.7``.

There are more usage options (enabling for many repositories
selected by location, configuring which files are scanned and
which expressions are updated). See extension README.rst or
https://foss.heptapod.net/mercurial/mercurial-update_version/
"""

# pylint: disable=unused-argument,no-self-use,too-few-public-methods

from mercurial import commands, scmutil, node, error
from mercurial.i18n import _
try:
    # HG ≥ 4.7
    from mercurial.utils.dateutil import datestr
    from mercurial.utils.stringutil import shortuser
except (ImportError, AttributeError):
    # Older HG
    from mercurial.util import shortuser, datestr

import re
import os
import sys


def import_meu():
    """
    Import of mercurial_extension_utils.

    In case normal import fails, some workarounds are tried.
    """
    try:
        import mercurial_extension_utils
    except ImportError:
        my_dir = os.path.dirname(__file__)
        sys.path.extend([
            # In the same dir (manual or site-packages after pip)
            my_dir,
            # Developer clone
            os.path.join(os.path.dirname(my_dir), "extension_utils"),
            # Side clone
            os.path.join(os.path.dirname(my_dir), "mercurial-extension_utils"),
        ])
        try:
            import mercurial_extension_utils
        except ImportError:
            raise error.Abort(_("""Can not import mercurial_extension_utils.
Please install this module in Python path.
See Installation chapter in https://foss.heptapod.net/mercurial/mercurial-dynamic_username/ for details
(and for info about TortoiseHG on Windows, or other bundled Python)."""))
    return mercurial_extension_utils


meu = import_meu()  # pylint: disable=invalid-name

# pylint:disable=fixme,line-too-long,invalid-name
#   (invalid-name because of ui and cmdtable)

############################################################
# Interfaces / base classes
############################################################


class Language(object):
    """Language rules (files to scan, syntax to find)."""

    def repo_setup(self, ui, repo):
        """
        Initialize access to repository.

        Called before first action on given repo, once.
        Can prepare (and save on this object attributes) some
        repository-state-level data (like info about the current
        revision or hgrc-based config param).
        """
        pass

    def size_limit(self):
        """
        Max size of the file being edited.

        Bigger files are skipped. Rather small by default (we mostly
        use small files like version.py) but some languages override this
        to allow bigger values.
        """
        return 16384

    def format_version_no(self, version_parts):
        """
        To be overridden. Formats version string to be used in code.

        :param version_parts: tuple like ("1", "2") or ("1", "7", "04")
                - version number extracted from tag
        :return: formatted string appropriate for language or None
                 if given version is invalid for it (too short, to long etc)
        """
        raise error.Abort(_("Not implemented"))

    def worth_checking(self, repo_path, repo_root):
        """
        Decide whether the file should be checked (mostly by name).

        To be overridden.  Checks whether given file should be checked
        (matches name pattern, has proper depth in repo dirtree etc).
        Called by default locate_files, not used if locate_files is
        overridden.

        Optionally can also set some limits on file processing
        (checked expressions count, max line number). In such a case,
        the following dictionary should be returned::

            {
                'max_line_no': 20,
                'max_expr_no': 1
            }

        where ``max_line_no`` specifies line limit (here: only lines 1-20
        can be changed) and ``max_expr_no`` matching expression limit
        (here: only first expression is to be updated, remaning are
        to be ignored). Any of those keys can be skipped meaning
        no appropriate restriction.

        Note: items of this dictionary finally land as update_file arguments.

        :param repo_path: File name (relative to repo root), as binary string
        :param repo_root: Repository root (full path), as binary string

        :return: False if file is to be skipped, True if should
            be considered and checked withiut restrictions,
            dictionary if file should be checked but there are
            some restrictions.
        """
        raise error.Abort(_("Not implemented"))

    def locate_files(self, ui, repo):
        """
        Find files to verify.

        Yields all files, which should be checked.

        Can be overridden, by default iterates over all repository
        files (as returned by manifest) and filters them by worth_checking
        and by size limit.

        Works as generator, yields triples::

            "path/vs/repo/root", "/full/path", {restrictions}

        where restrictions is dictionary of additional restrictions as
        described in extended worth_checking reply. The latter dictionary
        can be empty if there are no restrictions.
        """
        size_limit = self.size_limit()
        for repo_path in sorted(self.manifest(repo)):
            wrth = self.worth_checking(repo_path, repo.root)
            if wrth:
                full_path = os.path.join(repo.root, repo_path)
                size = os.path.getsize(full_path)
                if size <= size_limit:
                    if not isinstance(wrth, dict):
                        wrth = {}
                    yield repo_path, full_path, wrth
                else:
                    ui.debug(meu.ui_string(
                        "update_version: Ignoring big file %s (%s bytes > %s limit)\n",
                        repo_path, size, size_limit))

    def update_line(self, line, version, repo_path):
        """
        Update single line (fix version number if present).

        To be overridden. Called by default update_file.

        :param line: complete input line, without final newline
        :param version: version number to save, whatever
               format_version_no returned
        :param repo_path: File name (relative to repo root)
        :return: updated line or None if no changes were needed
               (return updated line if it already contains proper
               version number). Returned value should not have final newline
        """
        raise error.Abort(_("Not implemented"))

    def update_file(self, ui, repo, repo_path, full_path, version, dry_run=False, max_line_no=None, max_expr_no=None):
        """
        Update given file (fix found version numbers).

        Iterates over file lines and calls update_line

        :param full_path: file to edit, full absolute path
        :param repo_path: file to edit, relative repo root
        :param version: version number, whatever format_version_no
            returned
        :param dry_run: does not save
        :param max_line_no: limit checking to that many lines
        :param max_expr_no: limit checking to that many expressions

        :return: list of triples (lineno, before, after) - before and after as bytes
        """
        file_lines = []
        changes = []
        # basename = os.path.basename(repo_path)

        expr_count = 0
        with open(full_path, "rb") as input_fd:
            line_no = 0
            for line in input_fd:
                line_no += 1
                stripped_line = line.rstrip(b"\r\n")
                fixed_line = self.update_line(stripped_line, version, repo_path)
                if fixed_line is None:
                    file_lines.append(line)
                else:
                    # Reintroduce final newline
                    fixed_line += line[len(stripped_line):]
                    file_lines.append(fixed_line)
                    if fixed_line != line:
                        changes.append((line_no, line, fixed_line))
                    else:
                        ui.status(meu.ui_string(
                            "update_version: Line %s in %s already contains proper version number\n",
                            line_no, repo_path))
                    expr_count += 1
                if (max_line_no and line_no >= max_line_no) or (max_expr_no and expr_count >= max_expr_no):
                    # Rest of the file to be left as-is. We must read the rest only if there are some changes
                    # (elsewhere we don't need file_lines)
                    if changes:
                        for fin_line in input_fd:
                            file_lines.append(fin_line)
                    break

        if changes:
            if not dry_run:
                with open(full_path, "wb") as output:
                    output.writelines(file_lines)
        return changes

    def manifest(self, repo):
        """Helper. Yields names (repo-root-relative) of all repository files, as binary strings."""
        ctx = repo[b'.']
        for fname in ctx.manifest():
            yield fname


class TagFmt(object):
    """Tag numbering format representation."""

    sample = ""

    def extract_no(self, tag_text):
        """
        Extract actual, parsed tag number, extracted from the tag.

        Returns tag number or None if tag does not match pattern.

        :param tag_text: whatever used gave
        :return: tag number as string tuple like ``("1","0","2")`` or ``("3","08")``
             or ``None``
        """
        raise error.Abort(_("Not implemented"))


############################################################
# Languages
############################################################

known_languages = {}


class LanguagePython(Language):
    """Python language rules."""

    tested_file_names = [b'setup.py', b'version.py', b'__init__.py']

    def format_version_no(self, version_parts):
        return ".".join(str(vp) for vp in version_parts)

    def worth_checking(self, repo_path, repo_root):
        return os.path.basename(repo_path) in self.tested_file_names

    def update_line(self, line, version, repo_path):
        match = self.re_version_line.search(line)
        if match:
            return match.group('before') + version + match.group('after')
        else:
            return None

    re_version_line = re.compile(b'''
    ^   (?P<before>
             \\s* VERSION \\s* = \\s*
             (?P<quote> ["'] )      )
        (?P<version> \\d+(?:\\.\\d+)+  )
        (?P<after>
             (?P=quote)   # closing quote
             .* )
    $ ''', re.VERBOSE)


known_languages['python'] = LanguagePython()


class LanguagePerl(Language):
    """Perl language rules."""

    def format_version_no(self, version_parts):
        if len(version_parts) == 2:
            return ".".join(version_parts)
        if len(version_parts) == 3:
            txt = version_parts[0] + "."
            for item in version_parts[1:]:
                if len(item) > 2:
                    return None
                txt += "0" * (2 - len(item)) + item
            return txt
        return None

    def worth_checking(self, repo_path, repo_root):
        return repo_path.endswith(b".pm") \
            or repo_path.endswith(b".pl") \
            or repo_path.endswith(b".pod") \
            or os.path.basename(repo_path) == b"dist.ini"

    def update_line(self, line, version, repo_path):
        if repo_path.endswith(b".ini"):
            rgxps = self.re_ini_rgxps
        else:
            rgxps = self.re_perl_rgxps
        for rgxp in rgxps:
            match = rgxp.search(line)
            if match:
                return match.group('before') + version + match.group('after')
        return None

    re_ini_rgxps = [
        re.compile(b'''
        ^   (?P<before>
                 \\s* version \\s* = \\s*  )
        (?P<version> \\d+(?:\\.\\d+)+  )
        (?P<after>
             \\s*  (?:\\#.*)?  )
        $ ''', re.VERBOSE),
    ]

    re_perl_rgxps = [
        re.compile(b'''
        ^  (?P<before>
               \\s* (?: my | our | ) \\s*
               \\$ VERSION \\s* = \\s*
               (?P<quote> ["'] )         )
           (?P<version> \\d+\\.\\d+         )
           (?P<after>
               (?P=quote)   # closing quote
               .* )
        $ ''', re.VERBOSE),
        re.compile(b'''
        ^  (?P<before>
               \\s* use \\s+ constant \\s+ VERSION \\s* => \\s*
               (?P<quote> ["'] )         )
           (?P<version> \\d+\\.\\d+         )
           (?P<after>
               (?P=quote)   # closing quote
               .* )
        $ ''', re.VERBOSE),
        re.compile(b'''
        ^  (?P<before> \\s* Version \\s+ )
           (?P<ver> \\d+\\.\\d+           )
           (?P<after> \\s*              )
           $
        ''', re.VERBOSE),
    ]


known_languages['perl'] = LanguagePerl()


class LanguageJavaScript(Language):
    """JavaScript language rules."""

    def format_version_no(self, version_parts):
        return ".".join(version_parts)

    def worth_checking(self, repo_path, repo_root):
        return repo_path.endswith(b"version.js") \
            or repo_path.endswith(b"version.jsx") \
            or os.path.basename(repo_path) == b"package.json"

    def update_line(self, line, version, repo_path):
        if repo_path.endswith(b".json"):
            rgxps = self.re_json_rgxps
        else:
            rgxps = self.re_js_rgxps
        for rgxp in rgxps:
            match = rgxp.search(line)
            if match:
                return match.group('before') + version + match.group('after')
        return None

    re_json_rgxps = [
        re.compile(b'''
        ^
        (?P<before>
             \\s* (?P<quote> ["'] )  version (?P=quote)
             \\s* : \\s*
             (?P<quote2> ["'] )
        )
        (?P<version> \\d+(?:\\.\\d+)+  )
        (?P<after>
             \\s* (?P=quote2) \\s* ,? \\s*
        )
        $''', re.VERBOSE),
    ]

    re_js_rgxps = [
        re.compile(b'''
        ^  (?P<before>
               \\s* (?: const | var | let ) \\s+
               VERSION \\s* = \\s*
               (?P<quote> ["'] )         )
           (?P<version> \\d+(?:\\.\\d+)*    )
           (?P<after>
               (?P=quote)   # closing quote
               .* )
        $ ''', re.VERBOSE),
    ]


known_languages['javascript'] = LanguageJavaScript()


class LanguageJSON(Language):
    """JSON language rules."""

    def format_version_no(self, version_parts):
        return ".".join(version_parts)

    def size_limit(self):
        # Configlike JSON's happen to be big (my use-case is Elastic mapping definition).
        return 262144

    def worth_checking(self, repo_path, repo_root):
        if repo_path.endswith(b".json"):
            return {
                'max_line_no': 30,
                'max_expr_no': 1
            }
        else:
            return False

    def update_line(self, line, version, repo_path):
        rgxps = self.re_json_rgxps
        for rgxp in rgxps:
            match = rgxp.search(line)
            if match:
                return match.group('before') + version + match.group('after')
        return None

    re_json_rgxps = LanguageJavaScript.re_json_rgxps


known_languages['json'] = LanguageJSON()


class LanguageCxx(Language):
    """C++ language rules."""

    def format_version_no(self, version_parts):
        return ".".join(version_parts)

    _re_fname = re.compile(b'^version\\.(cxx|cpp|hxx|hpp)$')

    def worth_checking(self, repo_path, repo_root):
        base = os.path.basename(repo_path)
        match = self._re_fname.search(base)
        return bool(match)

    def update_line(self, line, version, repo_path):
        for rgxp in self.re_const_rgxps:
            match = rgxp.search(line)
            if match:
                return match.group('before') + version + match.group('after')
        return None

    re_const_rgxps = [
        # Zapisy z =
        re.compile(b'''
        ^  (?P<before>
               \\s* (?: const \\s+ )?
               (?: string \\s+ | char \\s* \\* \\s* | char \\s+)
               VERSION
               (?: \\[\\s*\\]  )?
               \\s* = \\s*
               (?P<quote> ["'] )         )
           (?P<version> \\d+(?:\\.\\d+)*    )
           (?P<after>
               (?P=quote)   # closing quote
               .* )
        $ ''', re.VERBOSE),
        # Zapisy z ()
        re.compile(b'''
        ^  (?P<before>
               \\s* (?: const \\s+ )?
                   string
               \\s+
               VERSION
               \\s* \\(
               (?P<quote> ["'] )         )
           (?P<version> \\d+(?:\\.\\d+)*    )
           (?P<after>
               (?P=quote)   # closing quote
               .* )
        $ ''', re.VERBOSE),
    ]


known_languages['c++'] = LanguageCxx()


class LanguageLogstash(Language):
    """Logstash language rules."""

    def format_version_no(self, version_parts):
        return ".".join(version_parts)

    _re_fname = re.compile(b'.*version.*\\.conf$')

    def worth_checking(self, repo_path, repo_root):
        base = os.path.basename(repo_path)
        match = self._re_fname.search(base)
        return bool(match)

    def update_line(self, line, version, repo_path):
        for rgxp in self.re_const_rgxps:
            match = rgxp.search(line)
            if match:
                return match.group('before') + version + match.group('after')
        return None

    re_const_rgxps = [
        # Zapisy z =
        re.compile(b'''
        ^  (?P<before>
               \\s* add_field
               \\s* => \\s*
               { \\s*
               (?P<quotekey> ["'] )
                   .* \\[version\\]
               (?P=quotekey)   # closing quote
               \\s* => \\s*
               (?P<quote> ["'] )
           )
           (?P<version>
               \\d+(?:\\.\\d+)*
           )
           (?P<after>
               (?P=quote)   # closing quote
               \\s* }
           )
        $ ''', re.VERBOSE),
    ]


known_languages['logstash'] = LanguageLogstash()


class LanguageYAML(Language):
    """YAML language rules."""

    def format_version_no(self, version_parts):
        return ".".join(version_parts)

    def size_limit(self):
        return 262144

    def worth_checking(self, repo_path, repo_root):
        if repo_path.endswith(b".yml") or repo_path.endswith(b".yaml"):
            return {
                'max_line_no': 20,
                'max_expr_no': 1
            }
        else:
            return False

    def update_line(self, line, version, repo_path):
        rgxps = self.re_yaml_rgxps
        for rgxp in rgxps:
            match = rgxp.search(line)
            if match:
                return match.group('before') + version + match.group('after')
        return None

    re_yaml_rgxps = [
        re.compile(b'''
        ^
        (?P<before>
             \\s* (?: module_ | package_ | )  version
             \\s* : \\s*
             (?P<quote2> ["']? )
        )
        (?P<version> \\d+(?:\\.\\d+)+  )
        (?P<after>
             \\s* (?P=quote2) \\s*
        )
        $''', re.VERBOSE),
    ]


known_languages['yaml'] = LanguageYAML()


class LanguageCvsKeywords(Language):
    """
    Support for handling CVS keywords.

    It doesn't really is a language, but using the same base class
    saves some work as we can reuse similar bits of implementation.
    """

    def repo_setup(self, ui, repo):
        self.current_rev = scmutil.revsingle(repo, b'.')
        # mercurial.context.changectx

        # For Author we take tagging user (it's not worth it to
        # detect last changes for all files and he is to commit them
        # after all)
        # …  self.current_rev.user()
        self.current_fmt_user = shortuser(ui.username())

    def size_limit(self):
        return 16384 * 1024

    def format_version_no(self, version_parts):
        return ".".join(str(vp) for vp in version_parts)

    def worth_checking(self, repo_path, repo_root):
        return True

    def update_line(self, line, version, repo_path):
        def _replace(match):
            kw = match.group(1)
            resolver = '_resolve_' + meu.pycompat.sysstr(kw)
            value = None
            if hasattr(self, resolver):
                value = getattr(self, resolver)(version, repo_path)
            if value:
                return b'$' + kw + b': ' + value + b' $'
            else:
                return b'$' + kw + b'$'

        new_line = self.re_keyword.sub(_replace, line)
        if new_line == line:
            return None
        else:
            # print "DBG: swapped\n%s\nto:\n%s\n" % (line, new_line)
            return new_line

    def _resolve_Name(self, version, repo_path):
        # $Name: 0.7.0 $
        return meu.pycompat.bytestr(version)

    def _resolve_Revision(self, version, repo_path):
        # $Revision: 9754f628932a $
        return node.short(node.bin(self.current_rev.hex()))

    def _resolve_Header(self, version, repo_path):
        # $Header: mercurial_update_version.py,v 9754f628932a 2017/01/09 00:12:41 Marcin Exp $
        return b" ".join([
            self._resolve_Source(version, repo_path),
            self._resolve_Revision(version, repo_path),
            self._resolve_Date(version, repo_path),
            self._resolve_Author(version, repo_path),
            self._resolve_State(version, repo_path),
        ])

    def _resolve_Id(self, version, repo_path):
        # $Id: mercurial_update_version.py,v 9754f628932a 2017/01/09 00:12:41 Marcin Exp $
        return b" ".join([
            self._resolve_RCSFile(version, repo_path),
            self._resolve_Revision(version, repo_path),
            self._resolve_Date(version, repo_path),
            self._resolve_Author(version, repo_path),
            self._resolve_State(version, repo_path),
        ])

    def _resolve_Source(self, version, repo_path):
        # $Source: mercurial_update_version.py,v $
        return repo_path + b",v"

    def _resolve_RCSFile(self, version, repo_path):
        # $RCSfile: keyword.html,v $
        return os.path.basename(repo_path) + b",v"

    def _resolve_Author(self, version, repo_path):
        # $Author: Marcin $
        return meu.pycompat.bytestr(self.current_fmt_user)

    def _resolve_Date(self, version, repo_path):
        # $Date: 2017/01/09 00:12:41 $
        d = self.current_rev.date()
        return datestr(d, format=b"%Y/%m/%d %H:%M:%S")

    def _resolve_State(self, version, repo_path):
        # $State: Exp $
        # Some claim Stab or Rel could happen…
        return b'Exp'

    re_keyword = re.compile(b'''
    \\$
    (Name|Revision|Header|Id|Source|RCSFile|Author|Date)
    (?:
    : [^\\$]*
    )?
    \\$
    ''', re.VERBOSE)


############################################################
# Tag formats
############################################################

known_tagfmts = {}


class TagFmtDotted(TagFmt):
    """Dotted (``1.2.3``) tag format."""

    sample = "1.3.11"
    _re_tag = re.compile('^ ( \\d+ (?:\\.\\d+)+ )$', re.VERBOSE)

    def extract_no(self, tag_text):
        match = self._re_tag.search(tag_text)
        if match:
            return match.group(1).split(".")
        else:
            return None


known_tagfmts['dotted'] = TagFmtDotted()


class TagFmtDashed(TagFmt):
    """Dashed tag format (``1-2-3``, ``1-17`` etc)."""

    sample = "1-3-11"
    _re_tag = re.compile('^ ( \\d+ (?:-\\d+)+ )$', re.VERBOSE)

    def extract_no(self, tag_text):
        match = self._re_tag.search(tag_text)
        if match:
            return match.group(1).split("-")
        else:
            return None


known_tagfmts['dashed'] = TagFmtDashed()


class TagFmtPfxDotted(TagFmt):
    """Prefixed dotteg tag format (``mylib-1.3.11``, ``something_1.7``)."""

    sample = "mylib-1.3.11"
    _re_tag = re.compile('^ .* [_-] ( \\d+ (?:\\.\\d+)+ )$', re.VERBOSE)

    def extract_no(self, tag_text):
        match = self._re_tag.search(tag_text)
        if match:
            return match.group(1).split(".")
        else:
            return None


known_tagfmts['pfx-dotted'] = TagFmtPfxDotted()


class TagFmtPfxDashed(TagFmt):
    """Prefixed-dashed tag format (``abc_1-2-3``, ``xoxo-1-17`` etc)."""

    sample = "mylib_1-3-11"
    _re_tag = re.compile('^ .* [^\\d_-] .*? [-_] ( \\d+ (?:\\-\\d+)+ )$', re.VERBOSE)

    def extract_no(self, tag_text):
        match = self._re_tag.search(tag_text)
        if match:
            return match.group(1).split("-")
        else:
            return None


known_tagfmts['pfx-dashed'] = TagFmtPfxDashed()


############################################################
# Actual extension work
############################################################

class Mode(object):
    """Aggregated config for single repo."""

    def __init__(self, language, tagfmt, expand_keywords=False):
        """
        :param language: Language object (which files and constants we fix)
        :param tagfmt: TagFmt object (what tag format is in use)
        """
        self.language = language
        self.tagfmt = tagfmt
        self.expand_keywords = expand_keywords

    def __str__(self):
        """Simple diagnostic description."""
        dscrpt = []
        if self.language:
            dscrpt.append("using %s language rules and %s tag format" % (
                self.language, self.tagfmt))
        if self.expand_keywords:
            dscrpt.append("expanding CVS keywords")
        return ", ".join(dscrpt)


def modes_active_on(ui, repo):
    """
    Checks whether extension is to be active on given repo - and how.

    Returns list of matching Mode objects (which can be empty).
    """
    # Boring iteration over config

    def read_details(ui, language_tag, tagfmt_tag, expand_keywords_tag):
        """Read actual languagename+tagfmtname pair from configuration"""
        language = meu.pycompat.sysstr(ui.config(b"update_version", meu.pycompat.bytestr(language_tag), None) or '')
        tagfmt = meu.pycompat.sysstr(ui.config(b"update_version", meu.pycompat.bytestr(tagfmt_tag), None) or '')
        expand_keywords = ui.configbool(b"update_version", meu.pycompat.bytestr(expand_keywords_tag), False)

        ui.debug(meu.ui_string("update_version: config checked, %s=%s, %s=%s, %s=%s\n",
                               language_tag, language or '', tagfmt_tag, tagfmt or '',
                               expand_keywords_tag, str(expand_keywords)))

        if language and not tagfmt:
            ui.warn(meu.ui_string(
                "update_version: %s not set in [update_version] section\n",
                tagfmt_tag))
        if tagfmt and not language:
            ui.warn(meu.ui_string(
                "update_version: %s not set in [update_version] section\n",
                language_tag))
        if not language and not tagfmt and not expand_keywords:
            ui.warn(meu.ui_string(
                "update_version: Unconfigured, neither %s, nor %s set in [update_version] section",
                language_tag, expand_keywords))
            return None
        mode = Mode(language=language, tagfmt=tagfmt, expand_keywords=expand_keywords)
        return mode

    if not hasattr(repo, 'root'):
        return None

    modes = []

    # enabled by active=true
    if ui.configbool(b"update_version", b"active", False):
        ui.debug(meu.ui_string(
            "update_version: active on %s due to active=true\n",
            repo.root))
        modes.append(
            read_details(ui, "language", "tagfmt", "expand_keywords"))

    # enabled by «label».active=true
    for name, items in meu.suffix_configlist_items(
            ui, "update_version", "active"):
        if ui.configbool(b"update_version", name + b".active", False):
            ui.debug(meu.ui_string(
                "update_version: active on %s due to %s.active=true\n",
                repo.root, name))
            modes.append(
                read_details(ui, name + b".language", name + b".tagfmt", name + b".expand_keywords"))

    # enabled by active_on=dirs
    active_on = ui.configlist(b"update_version", b"active_on", [])
    if active_on:
        if meu.belongs_to_tree_group(repo.root, active_on):
            ui.debug(meu.ui_string(
                "update_version: active on %s due to active_on=%s\n",
                repo.root, b", ".join(active_on)))
            modes.append(
                read_details(ui, b"language", b"tagfmt", b"expand_keywords"))
        else:
            ui.debug(meu.ui_string(
                "update_version: mismatch, %s does not match active_on=%s\n",
                repo.root, b", ".join(active_on)))

    # enabled by «label».active_on=dirs
    for name, items in meu.suffix_configlist_items(
            ui, "update_version", "active_on"):
        if meu.belongs_to_tree_group(repo.root, items):
            ui.debug(meu.ui_string(
                "update_version: active on %s due to %s.active_on=%s\n",
                repo.root, name, b", ".join(items)))
            modes.append(
                read_details(ui, name + b".language", name + b".tagfmt",
                             name + b".expand_keywords"))
        else:
            ui.debug(meu.ui_string(
                "update_version: mismatch, %s does not match %s.active_on=%s\n",
                repo.root, name, b", ".join(items)))

    return modes


def _apply_version_constants(ui, repo,
                             tag_name, language_name, tagfmt_name,
                             dry_run=False):
    """Peforms VERSION= changes, as necessary.

    Returns the pair:
    - list of changed files if sth changed, empty list if no changes,
      None if some error happened and was reported,
    - version constant (present if any files are modified)
    """
    language = known_languages.get(language_name)
    if not language:
        ui.warn(meu.ui_string(
            "update_version: Unknown language %s\n",
            language_name))
        return [], None
    tagfmt = known_tagfmts.get(tagfmt_name)
    if not tagfmt:
        ui.warn(meu.ui_string("update_version: Unknown tagfmt %s\n",
                tagfmt_name))
        return [], None

    version = tagfmt.extract_no(tag_name)
    if not version:
        ui.warn(meu.ui_string(
            "update_version: Invalid tag format: %s (expected %s, for example %s). Version not updated (but tag created).\n",
            tag_name, tagfmt_name, tagfmt.sample))
        return [], None  # means OK

    language.repo_setup(ui, repo)

    fmt_version = language.format_version_no(version)
    if not fmt_version:
        ui.warn(meu.ui_string(
            "update_version: Version number not supported by %s language: %s (too many parts or number too big)\n",
            language_name, ".".join(version)))
        return None, None  # means FAIL
    fmt_version = meu.pycompat.bytestr(fmt_version)

    # Apply version number on files
    changed_files = []
    for repo_path, full_path, restrictions in language.locate_files(ui, repo):
        changes = language.update_file(
            ui, repo, repo_path, full_path, fmt_version, dry_run, **restrictions)
        if changes:
            ui.status(meu.ui_string(
                "update_version: Version number in %s set to %s. List of changes:\n",
                repo_path, fmt_version))
            for lineno, before, after in changes:
                ui.status(meu.ui_string(
                    "    Line %s\n    < %s\n    > %s\n",
                    lineno, before.rstrip(b"\r\n"), after.rstrip(b"\r\n")))
            changed_files.append(full_path)
        else:
            ui.debug(meu.ui_string(
                "update_version: no changes in %s\n",
                repo_path))

    return changed_files, fmt_version


def _apply_cvs_keywords(ui, repo, tag_name, dry_run=False):
    # Apply version number on files
    language = LanguageCvsKeywords()

    language.repo_setup(ui, repo)

    changed_files = []
    changed_names = []
    for repo_path, full_path, restrictions in language.locate_files(ui, repo):
        changes = language.update_file(
            ui, repo, repo_path, full_path, tag_name, dry_run=dry_run, **restrictions)
        if changes:
            ui.debug(meu.ui_string(
                "update_version: CVS keywords in %s expanded. List of changes:\n",
                repo_path))
            for lineno, before, after in changes:
                ui.debug(meu.ui_string(
                    "    Line %s\n    < %s\n    > %s\n",
                    lineno, before.rstrip(b"\r\n"), after.rstrip(b"\r\n")))
            changed_files.append(full_path)
            changed_names.append(repo_path)

    if changed_files:
        ui.status(meu.ui_string(
            "update_version: CVS keywords expanded in %s\n",
            b" ".join(changed_names)))

    return changed_files


def update_repository(ui, repo, tag_name, dry_run=False):
    """Perform main actual action.

    :param ui: mercurial.ui.ui
    :param repo: repository object
    :param tag_name: actual tag, as str (``'4.72'``)
    """
    modes = modes_active_on(ui, repo)
    if not modes:
        return

    changed_files = []

    for mode in modes:
        ui.debug(meu.ui_string("update_version: processing mode: %s\n",
                               mode))

        # VERSION=…
        if mode.language:
            ver_changed_files, fmt_version = _apply_version_constants(
                ui, repo, tag_name,
                mode.language, mode.tagfmt, dry_run=dry_run)
            if ver_changed_files is None:
                return True  # means Fail
        else:
            ver_changed_files = []
            fmt_version = tag_name   # For commit message

        # $Keywords$
        if mode.expand_keywords:
            kw_changed_files = _apply_cvs_keywords(
                ui, repo, tag_name, dry_run=dry_run)
            if kw_changed_files is None:
                return True  # means Fail
        else:
            kw_changed_files = []

        changed_files += ver_changed_files
        changed_files += kw_changed_files

    if not changed_files:
        ui.status(meu.ui_string("update_version: no files changed\n"))
        return False  # means OK

    # Commit those changes
    if not dry_run:
        ui.note(meu.ui_string("update_version: Commiting updated version number\n"))
        commands.commit(         # pylint: disable=star-args
            ui, repo,
            *changed_files,
            message=meu.ui_string("Version number set to %s", fmt_version))

    return False  # means OK


############################################################
# Monkeypatching.
############################################################

# We avoid monkepatching if possible, so instead of doing this
# unconditionally, we do it when needed. Here we note whether
# we monkeypathed…
_tag_is_patched = False
# … and keep info whether this must be done just now
# (for safety we save which argument to ignore)
_ignore_rev = None


def _ensure_next_hg_tag_ignores_given_rev(repo, rev):
    """
    Makes sure next tag command will ignore rev argument if equal to param.

    This is workaround for problems in Mercurials on py3 (pre-tag hook isn't
    able to update options anymore).

    Used only on py3.
    """
    global _tag_is_patched, _ignore_rev
    if not _tag_is_patched:
        _tag_is_patched = True

        from mercurial import tags

        @meu.monkeypatch_function(tags)
        def tag(repo, names, node, *args, **kwargs):
            global _ignore_rev
            if _ignore_rev and _ignore_rev == node:
                # tags.tag expect canonicalized final binary rev
                node = scmutil.revsingle(repo, b'.').node()
                _ignore_rev = None
            return tag.orig(repo, names, node, *args, **kwargs)

    # TO be sure, let's save which rev is to be ignored
    _ignore_rev = scmutil.revsingle(repo, rev).node()


############################################################
# Mercurial extension hooks
############################################################

# Note: as we commit something (updated numbers), the whole action
# must work as pre-tag hook, not pretag! During pretag the changeset
# being tagged is already set (and tag would omit the number-updating
# commit).
#
# According to mercurial docs, pre- hooks should be set during uisetup
# phase, so we enable them during uisetup below…

def pre_tag_hook(ui, repo, hooktype, pats, opts, **kwargs):
    """
    Extension implementation - gateway to mercurial API.

    Hook called before tagging.

    :param ui: standard mercurial.ui.ui object
    :param repo:
    :param hooktype: hook kind (``b'pre-tag'``)
    :param pats: arguments (``[b'3.0.4']``)
    :param opts: named arguments (``{b'force': None, b'local': True, b'message': b'Some thing'}``)
    """
    # Check command arguments. Ignore local tags, tags removal,
    # tags placed by revision (hg tag -r ... sth) unless they point
    # to the current revision. Extract final tag value.
    if opts.get(b'local'):
        ui.status(meu.ui_string("update_version: ignoring local tag (version number not updated)\n"))
        return
    if opts.get(b'remove'):
        ui.status(meu.ui_string("update_version: ignoring tag removal (version number not updated)\n"))
        return
    if opts.get(b'rev'):
        # Generally we ignore tags by revision, but it makes sense
        # to handle hg tag -r ‹current-rev› (especially considering
        # TortoiseHg tags by rev when someone tags via gui). In this
        # case we must drop this argument.
        current_rev = scmutil.revsingle(repo, b'.').node()
        given_rev = scmutil.revsingle(repo, opts[b'rev']).node()
        if current_rev != given_rev:
            ui.status(meu.ui_string("update_version: ignoring tag placed -r revision (tag is placed, but version number not updated)\n"))
            return
        else:
            # We handle hg up -r ‹currentrev›, so we keep working as if this param was missing.
            # But we must convince actual hg tag to tag our commit with version number.
            # In mercurial running on python2 it suffices to overwrite 'rev' argument,
            # as it is forwarded to actual function. On python3 unfortunately this doesn't
            # work anymore, so we apply some monkeypatching.
            if meu.pycompat.ispy3:
                _ensure_next_hg_tag_ignores_given_rev(repo, opts[b'rev'])
            opts[b'rev'] = None
    if len(pats) != 1:
        ui.status(meu.ui_string("update_version: ignoring unexpected arguments (bad tag args?)\n"))
        return

    tag_name = meu.pycompat.sysstr(pats[0])
    update_repository(ui, repo, tag_name)

    return False  # means ok


def uisetup(ui):
    """Enable pre-tag hook."""
    meu.enable_hook(ui, "pre-tag.update_version", pre_tag_hook)


# def reposetup(ui, repo):
#     # Test
#     def fire_me(*args, **kwargs):
#         print "I am fired", args, kwargs
#     meu.enable_hook(ui, "pretag.test", fire_me)


############################################################
# Commands
############################################################

cmdtable = {}
command = meu.command(cmdtable)


@command(b"tag_version_test",
         [],
         b"tag_version_test TAG")
def cmd_tag_version_test(ui, repo, tag, **opts):
    """Dry-run, listing what would be changed."""
    modes = modes_active_on(ui, repo)
    if not modes:
        ui.status(meu.ui_string("update_version: not active in this repository\n"))
        return
    for mode in modes:
        ui.status(meu.ui_string("update_version: %s\n",
                                mode))

    update_repository(ui, repo, meu.pycompat.sysstr(tag), dry_run=True)


############################################################
# Extension setup
############################################################

testedwith = '2.7 2.9 3.0 3.3 3.6 3.7 3.8 4.0 4.1 4.2 4.3 4.5 4.6 4.7 4.8 5.0 5.1 5.2'
buglink = 'https://foss.heptapod.net/mercurial/mercurial-update_version/issues'
