#!/usr/bin/env python3

# standards
import re

# hublot
from hublot import retry_on_scraper_error


def test_basic_logging(client, server, captured_logs):
    client.get(f'{server}/hello')
    assert re.search(fr'^\[\w\w\w/\w{{13}}\]          {server}/hello\n$', captured_logs())
    client.get(f'{server}/hello')
    assert re.search(fr'^\[\w\w\w/\w{{13}}\] \[cached\] {server}/hello\n$', captured_logs())


def test_logging_courtesy_sleep(client, server, captured_logs):
    client.get(f'{server}/echo?x=1')
    assert re.search(fr'^\[\w\w\w/\w{{13}}\]          {server}/echo\?x=1\n$', captured_logs())
    client.get(f'{server}/echo?x=2')
    assert re.search(fr'^\[\w\w\w/\w{{13}}\] \[  5s  \] {server}/echo\?x=2\n$', captured_logs())


def test_logging_redirects(client, server, captured_logs):
    client.get(f'{server}/redirect/chain/1')
    assert re.search(
        r'^'
        fr'\[\w\w\w/\w{{13}}\]          {server}/redirect/chain/1\n'
        fr'\[\w\w\w/\w{{13}}\]          -> {server}/redirect/chain/2\n'
        fr'\[\w\w\w/\w{{13}}\]          -> {server}/redirect/chain/3\n'
        r'$',
        captured_logs(),
    )


def test_logging_on_retry(client, server, unique_key, captured_logs):
    @retry_on_scraper_error
    def scrape():
        client.get(f'{server}/fail-twice-then-succeed/{unique_key}')
        return 'ok'

    scrape()
    assert re.search(
        r'^'
        fr'\[\w\w\w/\w{{13}}\]          {server}/fail-twice-then-succeed/{unique_key}\n'
        'HTTPError: 500 .+ sleeping 1s\n'
        fr'\[\w\w\w/\w{{13}}\]          {server}/fail-twice-then-succeed/{unique_key}\n'
        'HTTPError: 500 .+ sleeping 5s\n'
        fr'\[\w\w\w/\w{{13}}\]          {server}/fail-twice-then-succeed/{unique_key}\n'
        r'$',
        captured_logs(),
    )
