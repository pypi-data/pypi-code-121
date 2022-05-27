#!/usr/bin/env python3

# standards
import re

# hublot
from hublot import Client


def test_default_user_agent(server):
    client = Client()
    user_agent = client.get(f'{server}/echo').json()['headers']['User-Agent']
    assert re.search(r'^hublot/[\d\.]+$', user_agent), user_agent


def test_user_agent_constructor_arg(server):
    client = Client(user_agent='Nyanya/10.8')
    user_agent = client.get(f'{server}/echo').json()['headers']['User-Agent']
    assert user_agent == 'Nyanya/10.8'


def test_user_agent_instance_attribute(server):
    client = Client()
    client.user_agent='Dwidwi/0.9'
    user_agent = client.get(f'{server}/echo').json()['headers']['User-Agent']
    assert user_agent == 'Dwidwi/0.9'


def test_user_agent_in_headers(server):
    client = Client()
    res = client.get(
        f'{server}/echo',
        headers={'User-Agent': 'Bwabwa/7.3'},
    )
    user_agent = res.json()['headers']['User-Agent']
    assert user_agent == 'Bwabwa/7.3'
