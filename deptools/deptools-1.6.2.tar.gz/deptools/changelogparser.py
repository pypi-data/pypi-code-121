'''Change Log Parser

This utility is capable of parsing Markdown files that follow the "keep a
change log" v1.0.0 format. More than one input file can be used simultaneously.
In this case, the logs are merged, but keep the dates, title and info from the
first file.

Usage:
  changelogparser version    (-i <input>)... [-o <out_file>]
  changelogparser tohtml     (-i <input>)... [-p] <output>
  changelogparser tomd       (-i <input>)... [-p] <output>
  changelogparser todeb      (-i <input>)... [-p] <package_name> <output>
  changelogparser expandspec (-i <input>)... [-p] <src_spec>     <output>
  changelogparser tospec     (-i <input>)... [-p] <output>
  changelogparser -h | --help
  changelogparser --version

Commands:
  version     Prints out the version number of the program based on the inputs.
  tohtml      Converts the inputs in an HTML file
  tomd        Converts the inputs in a .md file
  todeb       Converts the inputs in a .deb file
  expandspec  Completes the .spec file passed as argument by replacing any
              instance of "@VERSION@" with the version number of the change
              log, and adding the log entries at the end of the file

Options:
  -h --help     Show this screen.
  -p            Export internal (private) entries.
  --version     Show version.

'''

from collections import defaultdict, namedtuple
from enum import Enum
import datetime
import re

from docopt import docopt

from parsimonious.exceptions import ParseError
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


class EntryType(Enum):
    '''The types of changes'''
    Added = 1
    Changed = 2
    Deprecated = 3
    Removed = 4
    Fixed = 5
    Security = 6


# A reference to a ticket (e.g. #123 or libats#12), usually at the end of each
# entry
TicketRef = namedtuple(
    'TicketRef',
    [
        'number',  # type: int
        'repo',  # type: Optional[str]
    ])

# Represents an entry in a change log. The associated tickets may be an empty list
EntryLog = namedtuple(
    'EntryLog',
    [
        'internal',  # type: bool
        'text',  # type: str
        'tickets',  # type: List[TicketRef]
    ])

# A category of change logs for a given version
CategoryLog = namedtuple(
    'CategoryLog',
    [
        'entry_type',  # type: EntryType
        'logs',  # type: List[EntryLog]
    ])

# A version number that follows semantic versioning
VersionNumber = namedtuple(
    'VersionNumber',
    [
        'unreleased',  # type: bool
        'major',  # type: int
        'minor',  # type: int
        'patch',  # type: int
        'prerelease',  # type: str
        'build',  # type: str
    ])

# Represents the identity of a version log (version number,
# release date, etc.)
VersionInfo = namedtuple(
    'VersionInfo',
    [
        'version',  # type: VersionNumber
        'date',  # type: datetime.date
        'yanked',  # type: bool
    ])

# List of logs for version numbers
VersionLog = namedtuple(
    'VersionLog',
    [
        'info',  # type: VersionInfo
        'logs',  # type: List[CategoryLog]
    ])

# A complete change log file
ChangeLog = namedtuple(
    'ChangeLog',
    [
        'title',  # type: str
        'intro',  # type: str
        'logs',  # type: List[VersionLog]
    ])


class ChangeLogRuleVisitor(NodeVisitor):
    '''Parses keepachangelog.org v1.0.0 change logs'''
    grammar = Grammar(r"""
        changelog = h1 maybe_textparagraph versionlogs
        h1 = "# " textline _
        textline = ~".+"
        versionlogs = versionlog*
        versionlog = h2 categorylogs
        h2 = ( released_h2 / unreleased_h2 )
        released_h2 = "## " version " - " date maybe_yanked _
        version = "[" sv2_semver "]"
        date = number "-" number "-" number
        number = ~"[0-9]+"
        maybe_yanked = (~" \[YANKED\]"i)?
        unreleased_h2 = "## " ~"\[unreleased\]"i _
        categorylogs = categorylog*
        categorylog = h3 entries
        h3 = "### " word _
        word = ~"[\w]+"
        entries = entry+
        entry = "- " maybe_internal textparagraph maybe_ticketrefs _
        maybe_internal = (~"\[INTERNAL\]"i)?

        maybe_ticketrefs = ticketrefs?
        ticketrefs = "[" ticketref maybe_ticketref_list_end  "]"
        maybe_ticketref_list_end = ticketref_list_element*
        ticketref_list_element = _ "," _ ticketref
        ticketref = ~"[A-Za-z]*#[0-9]+"

        maybe_textparagraph = textparagraph?
        # `textparagraph` matches any text, and stops at either a dash or a
        # pound characters at the start of a line, or at an opening square
        # bracket
        textparagraph = ~"[^-#].+?((?=^-)|(?=^#)|\Z|(?=\[))"ms
        _ = meaningless*
        meaningless = ~"[\s]+"

        # SemVer 2.0.0
        sv2_semver = (sv2_semver_core_prerelease_build
                      / sv2_semver_core_prerelease
                      / sv2_semver_core_build
                      / sv2_version_core)
        sv2_semver_core_prerelease_build = sv2_version_core "-" sv2_pre_release "+" sv2_build
        sv2_semver_core_prerelease = sv2_version_core "-" sv2_pre_release
        sv2_semver_core_build = sv2_version_core "+" sv2_build
        sv2_version_core = sv2_major "." sv2_minor "." sv2_patch
        sv2_major = sv2_numeric_identifier
        sv2_minor = sv2_numeric_identifier
        sv2_patch = sv2_numeric_identifier
        sv2_pre_release = sv2_dot_separated_pre_release_identifiers
        sv2_dot_separated_pre_release_identifiers = (
            (sv2_pre_release_identifier "." sv2_dot_separated_pre_release_identifiers)
            / sv2_pre_release_identifier)
        sv2_build = sv2_dot_separated_build_identifiers
        sv2_dot_separated_build_identifiers = (
            (sv2_build_identifier "." sv2_dot_separated_build_identifiers)
            / sv2_build_identifier)
        sv2_pre_release_identifier = sv2_alphanumeric_identifier / sv2_numeric_identifier
        sv2_build_identifier = sv2_alphanumeric_identifier / sv2_digits
        sv2_alphanumeric_identifier = ((sv2_non_digit sv2_identifier_characters)
                                       / sv2_non_digit
                                       / (sv2_identifier_characters sv2_non_digit sv2_identifier_characters))
                                       / (sv2_identifier_characters sv2_non_digit)
        sv2_numeric_identifier = ("0"
                                  / (sv2_positive_digit sv2_digits)
                                  / sv2_positive_digit)
        sv2_identifier_characters = ((sv2_identifier_character sv2_identifier_characters)
                                     / sv2_identifier_character)
        sv2_identifier_character = sv2_digit / sv2_non_digit
        sv2_non_digit = sv2_letter / "-"
        sv2_digits = (sv2_digit sv2_digits) / sv2_digit
        sv2_digit = "0" / sv2_positive_digit
        sv2_positive_digit = "1" / "2" / "3" / "4" / "5" / "6" / "7" / "8" / "9"
        sv2_letter = ("A" / "B" / "C" / "D" / "E" / "F" / "G" / "H" / "I" / "J"
                      / "K" / "L" / "M" / "N" / "O" / "P" / "Q" / "R" / "S" / "T"
                      / "U" / "V" / "W" / "X" / "Y" / "Z" / "a" / "b" / "c" / "d"
                      / "e" / "f" / "g" / "h" / "i" / "j" / "k" / "l" / "m" / "n"
                      / "o" / "p" / "q" / "r" / "s" / "t" / "u" / "v" / "w" / "x"
                      / "y" / "z")
        """)

    def generic_visit(self, _, __):
        pass

    def visit_sv2_numeric_identifier(self, node, _):
        return int(node.text)

    def visit_sv2_version_core(self, node, childs):
        return {'major': childs[0], 'minor': childs[2], 'patch': childs[4]}

    def visit_sv2_semver_core_prerelease_build(self, node, childs):
        result = {}
        result.update(childs[0])
        result.update(childs[2])
        result.update(childs[4])
        return result

    def visit_sv2_semver_core_build(self, node, childs):
        result = {}
        result.update(childs[0])
        result.update(childs[2])
        return result

    def visit_sv2_semver_core_prerelease(self, node, childs):
        result = {}
        result.update(childs[0])
        result.update(childs[2])
        return result

    def visit_sv2_dot_separated_build_identifiers(self, node, _):
        return {'build': node.text}

    def visit_sv2_dot_separated_pre_release_identifiers(self, node, _):
        return {'prerelease': node.text}

    def visit_sv2_semver(self, node, childs):
        result = {}
        for child in childs:
            if child is None:
                continue
            result.update(child)
        return result

    def visit_maybe_textparagraph(self, node, _):
        if node.text:
            return node.text.strip()
        return ""

    def visit_textparagraph(self, node, _):
        return re.sub(r'\s*\n\s*', ' ', node.text.strip())

    def visit_maybe_internal(self, node, _):
        if node.text:
            return True
        return False

    def visit_entry(self, _, childs):
        return EntryLog(childs[1], childs[2], childs[3])

    def visit_maybe_ticketrefs(self, node, childs):
        if node.text:
            return childs[0]
        return []

    def visit_ticketrefs(self, _, childs):
        return [childs[1], *childs[2]]

    def visit_maybe_ticketref_list_end(self, _, childs):
        return childs

    def visit_ticketref_list_element(self, _, childs):
        return childs[3]

    def visit_ticketref(self, node, _):
        repo, sep, number = node.text.partition('#')
        if not sep:
            raise ValueError("Separator not found in {}".format(node.text))
        if repo:
            return TicketRef(int(number), repo)
        return TicketRef(int(number), None)

    def visit_entries(self, _, childs):
        return childs

    def visit_word(self, node, _):
        return node.text

    def visit_h3(self, _, childs):
        return EntryType[childs[1]]

    def visit_categorylog(self, _, childs):
        return CategoryLog(childs[0], childs[1])

    def visit_categorylogs(self, _, childs):
        return childs

    def visit_number(self, node, _):
        return int(node.text)

    def visit_maybe_yanked(self, node, _):
        if node.text:
            return True
        return False

    def visit_unreleased_h2(self, _, __):
        return VersionInfo(VersionNumber(True, 0, 0, 0, "", ""),
                           datetime.date.today(), False)

    def visit_date(self, _, childs):
        return datetime.date(childs[0], childs[2], childs[4])

    def visit_version(self, _, childs):
        ver = childs[1]
        return VersionNumber(False, ver['major'], ver['minor'], ver['patch'],
                             ver.get('prerelease', ''), ver.get('build', ''))

    def visit_released_h2(self, _, childs):
        return VersionInfo(childs[1], childs[3], childs[4])

    def visit_h2(self, _, childs):
        return childs[0]

    def visit_versionlog(self, _, childs):
        return VersionLog(childs[0], childs[1])

    def visit_versionlogs(self, _, childs):
        return childs

    def visit_textline(self, node, _):
        return node.text

    def visit_h1(self, _, childs):
        return childs[1]

    def visit_changelog(self, _, childs):
        return ChangeLog(childs[0], childs[1], childs[2])


def ticketref_text(ticketref: TicketRef):
    if ticketref.repo is not None:
        return "{}#{}".format(ticketref.repo, ticketref.number)
    return "#{}".format(ticketref.number)


def entry_text(entry: EntryLog, output_internal: bool):
    text = entry.text
    if output_internal and len(entry.tickets):
        text += " ["
        text += ", ".join([ticketref_text(t) for t in entry.tickets])
        text += "]"
    return text


def version_log_empty(vlog, output_internal=False):
    '''A version log is considered empty if it would not output any entry'''

    for categorylog in vlog.logs:
        for log in categorylog.logs:
            if not log.internal or output_internal:
                return False

    return True


def categorylogs_merge(logs):
    if not logs:
        return

    entrylogs = []
    for categorylog in logs:
        entrylogs = entrylogs + categorylog.logs

    return CategoryLog(logs[0].entry_type, entrylogs)


def versionlogs_merge(logs):
    if not logs:
        return

    # Create map from EntryType to List[CategoryLog]
    categorylogsmap = defaultdict(list)
    for versionlog in logs:
        for categorylog in versionlog.logs:
            categorylogsmap[categorylog.entry_type].append(categorylog)

    # Reduce map into List[CategoryLog]
    categorylogs = []
    for entry_type in categorylogsmap:
        categorylogs.append(categorylogs_merge(categorylogsmap[entry_type]))

    return VersionLog(logs[0].info, categorylogs)


def changelogs_merge(logs):
    if not logs:
        return

    # Create map from Version to List[VersionLog]
    versionlogsmap = defaultdict(list)
    for changelog in logs:
        for versionlog in changelog.logs:
            versionlogsmap[versionlog.info.version].append(versionlog)

    versionlogs = []
    for version in reversed(sorted(versionlogsmap)):
        versionlogs.append(versionlogs_merge(versionlogsmap[version]))

    return ChangeLog(logs[0].title, logs[0].intro, versionlogs)


def changelog_version(changelog):
    return changelog.logs[0].info.version

'''Returns true if left and right are two released version numbers and if left
is higher than right'''
def is_more_than(left, right):
    if left.unreleased or right.unreleased:
        return False
    lv = (left.major, left.minor, left.patch)
    rv = (right.major, right.minor, right.patch)
    return lv > rv

def check_date_and_version_ordering(changelog):
    # Verifies that dates and versions are in descending order in the change
    # log
    logs = changelog.logs
    if not len(logs):
        return  # Empty change log
    curver = logs[0].info.version
    curdate = logs[0].info.date
    for i in range(1, len(logs)):
        log = logs[i]
        ver = log.info.version
        date = log.info.date
        if is_more_than(ver, curver):
            raise ValueError(
                "Versions in change log are not descending. Log index {} has version {} but previous was {}"
                .format(i, ver, curver))
        curver = ver
        if date > curdate:
            raise ValueError(
                "Dates are not descending. Log index {} has date {} but previous was {}"
                .format(i, date, curdate))
        curdate = date


def version_string(version, show_unreleased=True):
    if show_unreleased and version.unreleased:
        return "Unreleased"
    out = "{}.{}.{}".format(version.major, version.minor, version.patch)
    if version.prerelease:
        out += "-{}".format(version.prerelease)
    if version.build:
        out += "+{}".format(version.build)
    return out


def changelog_to_html(changelog, output_internal=False):
    out = """<h1>{}</h1>
<p>{}</p>\n""".format(changelog.title, changelog.intro)

    for versionlog in changelog.logs:
        ver = versionlog.info.version
        dat = versionlog.info.date
        if ver.unreleased:
            out = out + "<h2>[Unreleased]</h2>\n"
        else:
            out = out + "<h2>[{}]".format(version_string(ver))
            out = out + " - " + "{}-{}-{}".format(dat.year, dat.month, dat.day)
            out = out + "</h2>\n"

        if version_log_empty(versionlog, output_internal):
            out = out + "<ul><li>No user-visible change</li></ul>\n"
            continue

        for cat in versionlog.logs:
            out = out + "<h3>{}</h3>\n".format(cat.entry_type.name)
            out = out + "<ul>\n"
            for entry in cat.logs:
                if entry.internal and not output_internal:
                    continue
                out = out + "    <li>{}</li>\n".format(
                    entry_text(entry, output_internal))
            out = out + "</ul>\n"
    return out


def changelog_to_md(changelog, output_internal=False):
    out = "# {}\n\n{}\n".format(changelog.title, changelog.intro)

    for versionlog in changelog.logs:
        ver = versionlog.info.version
        dat = versionlog.info.date
        if ver.unreleased:
            out = out + "\n## [Unreleased]"
        else:
            out = out + "\n## [{}]".format(version_string(ver))
            out = out + " - " + "{:04d}-{:02d}-{:02d}".format(
                dat.year, dat.month, dat.day)

        if version_log_empty(versionlog, output_internal):
            out = out + "\n- No user-visible change\n"
            continue

        for cat in versionlog.logs:
            out = out + "\n### {}".format(cat.entry_type.name)
            for entry in cat.logs:
                if entry.internal:
                    if output_internal:
                        out = out + "\n- [Internal] {}".format(
                            entry_text(entry, output_internal))
                else:
                    out = out + "\n- {}".format(
                        entry_text(entry, output_internal))
            out = out + "\n"
    return out


def changelog_to_deb(changelog, package_name, output_internal=False):
    out = ""
    for versionlog in changelog.logs:
        ver = versionlog.info.version
        dat = versionlog.info.date
        out = out + "{} ({}) UNRELEASED; urgency=medium\n\n".format(
            package_name, version_string(ver, False))

        if version_log_empty(versionlog, output_internal):
            out = out + "  * No user-visible change\n"
        else:
            for cat in versionlog.logs:
                for entry in cat.logs:
                    if entry.internal and not output_internal:
                        continue
                    out = out + "  * {}: {}\n".format(
                        cat.entry_type.name, entry_text(
                            entry, output_internal))

        out = out + "\n -- AlazarTech <support@alazartech.com>  {} 12:12:00 -0400\n\n".format(
            dat.strftime('%a, %d %b %Y'))
    return out


def expand_spec(changelog, input_text, output_internal=False):
    out = input_text.replace("@VERSION@",
                             version_string(changelog_version(changelog)))
    for versionlog in changelog.logs:
        dat = versionlog.info.date
        ver = versionlog.info.version
        out = out + "* {} AlazarTech <support@alazartech.com>\n".format(
            dat.strftime('%a %b %d %Y'))
        out = out + "- Version {}\n".format(version_string(ver))

        if version_log_empty(versionlog, output_internal):
            out = out + "- No user-visible change\n"
            continue

        for cat in versionlog.logs:
            for entry in cat.logs:
                if entry.internal and not output_internal:
                    continue
                out = out + "- {}: {}\n".format(
                    cat.entry_type.name, entry_text(entry, output_internal))

    return out


def parse_changelog(filename):
    visitor = ChangeLogRuleVisitor()
    with open(filename, 'r') as clfile:
        return visitor.parse(clfile.read())


def main():
    arguments = docopt(__doc__, version='ChangeLog Parser')

    inputs = []
    visitor = ChangeLogRuleVisitor()
    for filename in arguments['<input>']:
        with open(filename, 'r') as clfile:
            inputs.append(visitor.parse(clfile.read()))

    changelog = changelogs_merge(inputs)
    check_date_and_version_ordering(changelog)

    if arguments['version']:
        ver = version_string(changelog_version(changelog))
        if arguments['-o']:
            with open(arguments['<out_file>'], 'w') as outf:
                outf.write(ver)
        else:
            print(ver)

    if arguments['tohtml']:
        output = changelog_to_html(changelog, arguments['-p'])
        with open(arguments['<output>'], 'w') as outf:
            outf.write(output)

    if arguments['tomd']:
        output = changelog_to_md(changelog, arguments['-p'])
        with open(arguments['<output>'], 'w') as outf:
            outf.write(output)

    if arguments['todeb']:
        output = changelog_to_deb(changelog, arguments['<package_name>'],
                                  arguments['-p'])
        with open(arguments['<output>'], 'w') as outf:
            outf.write(output)

    if arguments['expandspec']:
        input_text = ""
        with open(arguments['<src_spec>'], 'r') as inf:
            input_text = inf.read()

        output = expand_spec(changelog, input_text, arguments['-p'])
        with open(arguments['<output>'], 'w') as outf:
            outf.write(output)

    if arguments['tospec']:
        output = expand_spec(changelog, "", arguments['-p'])
        with open(arguments['<output>'], 'w') as outf:
            outf.write(output)


if __name__ == '__main__':
    main()
