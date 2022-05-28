import argparse
import importlib.metadata
import logging
import os
import queue
import threading
from urllib.parse import urlparse

import ghm

META = importlib.metadata.metadata(__package__)


def parse():
    parser = argparse.ArgumentParser(
        prog=META["Name"],
        description=META["Summary"],
        epilog=f"{META['Author']} <{META['Author-email']}>",
    )
    parser.add_argument("path", help="path for local mirrors")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{META['Name']} {META['Version']}",
    )

    auth_group = parser.add_argument_group("authentication")
    default_token = ghm.discover_token()
    token_env = f"(default: ${default_token.env})" if default_token.env else ""
    auth_group.add_argument(
        "-t",
        "--token",
        default=default_token.val,
        help=f"github access token {token_env}",
    )

    discovery_group = parser.add_argument_group("repository discovery")
    discovery_group.add_argument(
        "-u", "--user", help="discover repositories by username"
    )
    discovery_group.add_argument(
        "-o", "--org", help="discover repositories by organization"
    )

    filter_group = parser.add_argument_group("repository regexp filtering")
    filter_group.add_argument("--match-owner", help="include repositories by owner")
    filter_group.add_argument("--match-repo", help="include repositories by name")
    filter_group.add_argument("--exclude-owner", help="exclude repositories by owner")
    filter_group.add_argument("--exclude-repo", help="exclude repositories by name")
    filter_group.add_argument(
        "--exclude-forks", action="store_true", help="exclude forks"
    )

    perf_group = parser.add_argument_group("performance")
    default_workers = os.cpu_count()
    perf_group.add_argument(
        "--workers",
        default=default_workers,
        help=f"number of mirror workers to run (default: {default_workers})",
    )

    debug_group = parser.add_argument_group("debugging")
    default_log = "info"
    debug_group.add_argument(
        "-l",
        "--log-level",
        choices=("debug", "info", "warning", "error", "critical"),
        default=default_log,
        help=f"show messages of this level or higher (default: {default_log})",
    )
    debug_group.add_argument(
        "--dry-run",
        action="store_true",
        help="show what will happen without making changes",
    )

    options = parser.parse_args()

    token_url = urlparse(options.token)
    if token_url.scheme == "file":
        with open(token_url.path, "r") as f:
            options.token = f.read().strip()

    if options.dry_run:
        log_format = "[%(levelname)s] (DRY-RUN) %(message)s"
    else:
        log_format = "[%(levelname)s] %(message)s"

    log_level = getattr(logging, options.log_level.upper())
    logging.basicConfig(format=log_format, level=log_level)

    options_list = []
    for k, v in sorted(vars(options).items()):
        if v and k in ["token"]:
            v = "<redacted>"
        options_list.append(f"{k}={repr(v)}")
    logging.debug(f"Options: {', '.join(options_list)}")

    return options


def main():
    opts = parse()

    all_repos = ghm.discover_repos(opts.token, opts.user, opts.org)
    repos = ghm.filter_repos(
        all_repos,
        match_owner=opts.match_owner,
        match_repo=opts.match_repo,
        exclude_owner=opts.exclude_owner,
        exclude_repo=opts.exclude_repo,
        exclude_forks=opts.exclude_forks,
    )

    git_credentials = ghm.git_credentials_callback(token=opts.token)

    q = queue.Queue()
    for repo in repos:
        q.put(repo)

    def worker():
        while not q.empty():
            repo = q.get()
            path = ghm.clone_path(opts.path, repo)
            cloned = ghm.clone_repo(
                repo, path, callbacks=git_credentials, dry_run=opts.dry_run
            )
            if not cloned:
                ghm.fetch_repo(path, callbacks=git_credentials, dry_run=opts.dry_run)
            q.task_done()

    for i in range(opts.workers):
        threading.Thread(target=worker, daemon=True).start()

    q.join()
