# -*- coding: utf-8 -*-
import re
from types import SimpleNamespace

from blessed import Terminal

term = Terminal()


def repo_output_handler(repo, tabs=1, indent='\t'):

    results = []
    repo_condition = 'green'
    for i in repo.modified:
        results.append(term.yellow(f'{tabs*indent}modified: {i.path}'))
        repo_condition = 'yellow'
    for i in repo.renamed:
        results.append(
            term.yellow(f'{tabs*indent}renamed: {i.path} {i.original_path}')
        )
        repo_condition = 'yellow'
    for i in repo.untracked:
        results.append(term.yellow(f'{tabs*indent}untracked: {i.path}'))
        repo_condition = 'yellow'
    for i in repo.deleted:
        results.append(term.red(f'{tabs*indent}deleted: {i.path}'))
        repo_condition = 'red'
    for i in repo.ignored:
        results.append(term.red(f'{tabs*indent}ignored: {i.path}'))

    if not repo.online:
        repo_condition = 'blue'

    try:
        header = [(tabs - 1) * indent, repo.name]
        if repo.branch.head:
            header.append(term.magenta(repo.branch.head))
        if repo.ahead:
            header.append(term.cyan(f'↑{repo.ahead}'))
        if repo.behind:
            header.append(term.cyan(f'↓{repo.ahead}'))
        if repo.modified:
            header.append(term.cyan(f'~{len(repo.modified)}'))
        if repo.deleted:
            header.append(term.cyan(f'-{len(repo.deleted)}'))
        if repo.untracked:
            header.append(term.cyan(f'…{len(repo.untracked)}'))
        header = ' '.join(header)
    except Exception:  # For Bare Repos
        header = f"{(tabs-1)*indent} {repo.name} {len(repo.modified):+}"

    conditions = {
        "green": lambda iterable, item: iterable.insert(
            0, term.green(f"✓ {item}")
        ),
        "yellow": lambda iterable, item: iterable.insert(
            0, term.yellow(f"⚠ {header}")
        ),
        "red": lambda iterable, item: iterable.insert(
            0, term.red(f"! {header}")
        ),
        "blue": lambda iterable, item: iterable.insert(
            0, term.blue(f"? {header}")
        ),
        "default": lambda iterable, item: iterable.insert(0, f"? {header}"),
    }
    add_header = conditions.get(repo_condition, conditions['default'])
    add_header(results, header)

    return '\n'.join(results)


async def parse_repo(parsed_output: dict, short: bool = False):
    status_stdout = parsed_output['status']['stdout']
    parsed = parse_git_status(status_stdout)
    parsed.name = parsed_output['name']

    if short:
        # To tell if there's any changes that were made.
        any_changes = any(
            i
            for i in [
                parsed.ahead,
                parsed.behind,
                len(parsed.modified),
                len(parsed.renamed),
                len(parsed.deleted),
                len(parsed.untracked),
                len(parsed.ignored),
            ]
        )
        if any_changes:
            print(repo_output_handler(parsed))
    else:
        print(repo_output_handler(parsed))


def parse_git_status(stdout):

    lines = stdout.splitlines()
    repo = SimpleNamespace()

    branch_info = [i for i in lines if i.startswith('#')]
    modified = [i for i in lines if i.startswith('1')]
    renamed_or_copied = [i for i in lines if i.startswith('2')]
    untracked = [i for i in lines if i.startswith('?')]
    ignored = [i for i in lines if i.startswith('!')]

    # Branch
    oid_group = '# branch.oid (?P<oid>.*)'
    head_group = '# branch.head (?P<head>.*)'
    upstream_group = '# branch.upstream (?P<upstream>.*)'
    ahead_behind_group = '# branch.ab (?P<ahead>.*) (?P<behind>.*)'
    space = r'\s*'
    branch_re = re.compile(
        fr'({oid_group})?'
        + fr'{space}'
        + fr'({head_group})?'
        + fr'{space}'
        + fr'({upstream_group})?'
        + fr'{space}'
        + fr'({ahead_behind_group})?'
    )

    branch_info = [i for i in lines if i.startswith('#')]
    branch_match = branch_re.match('\n'.join(branch_info))

    branch = SimpleNamespace(
        oid=branch_match.group('oid'),
        head=branch_match.group('head'),
        upstream=branch_match.group('upstream'),
        ahead=int(
            branch_match.group('ahead') if branch_match.group('ahead') else 0
        ),
        behind=int(
            branch_match.group('behind') if branch_match.group('behind') else 0
        ),
    )

    # Changed
    modified = [get_file_info(i.split(maxsplit=9)) for i in modified]

    # Renamed or Copied
    renamed_or_copied = [
        get_file_info(i.split(maxsplit=10)) for i in renamed_or_copied
    ]

    # Untracked
    untracked = [i.split(maxsplit=1)[1] for i in untracked]
    untracked = [SimpleNamespace(path=i, type='Untracked') for i in untracked]

    # Ignored
    # Only if `--ignored=matching` is included
    ignored = [i.split(maxsplit=1)[1] for i in ignored]
    ignored = [SimpleNamespace(path=i, type='Ignored') for i in ignored]

    # All Files
    all_files = modified + renamed_or_copied + untracked + ignored
    # Resort by Type
    modified = [i for i in all_files if i.type[0] == 'M']
    renamed = [i for i in all_files if i.type[0] == 'R']
    deleted = [i for i in all_files if i.type[0] == 'D']
    untracked = [i for i in all_files if i.type[0] == 'U']
    ignored = [i for i in all_files if i.type[0] == 'I']

    repo.branch = branch
    repo.ahead = branch.ahead
    repo.behind = branch.behind
    repo.modified = modified
    repo.renamed = renamed
    repo.deleted = deleted
    repo.untracked = untracked
    repo.ignored = ignored
    repo.all_changed_files = all_files

    # Quickfix
    if repo.branch.oid:
        repo.online = True
    else:
        repo.online = False

    return repo


def get_file_info(raw):

    if raw[0] == '1':
        type_ = 'changed'
    else:
        type_ = 'renamed_or_copied'
    raw = raw[1:]  # Get rid of the type as the docs don't refer to it.

    if type_ == 'renamed_or_copied':
        path = raw[8]
        original_path = raw[9]
    else:
        path = raw[7]
        original_path = None

    staged = False
    subtype = raw[0][-1] if raw[0][-1] != '.' else raw[0][0]
    if raw[0][0] == '.':
        staged = False
        subtype = raw[0][-1]
    elif raw[0][-1] == '.':
        staged = True
        subtype = raw[0][0]
    if subtype == 'D':
        subtype = 'Deleted'
    elif subtype == 'M':
        subtype = 'Modified'
    elif subtype == 'R':
        subtype = 'Renamed'

    file = SimpleNamespace(
        path=path,
        staged=staged,
        original_path=original_path,
        type=subtype,
    )

    return file
