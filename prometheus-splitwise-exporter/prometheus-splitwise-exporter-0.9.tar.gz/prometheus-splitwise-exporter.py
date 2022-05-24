#!/usr/bin/python3

# Simple prometheus exporter for splitwise
# Copyright (C) 2019 Jelmer Vernooij <jelmer@jelmer.uk>
# Licensed under the Apache-2.0 license.

import argparse
import json
import logging
import requests
import splitwise
import sys

from prometheus_client import (
    CollectorRegistry,
    Gauge,
    push_to_gateway,
    generate_latest,
    )

parser = argparse.ArgumentParser('prometheus-splitwise-exporter')
parser.add_argument(
    '--prometheus', type=str, help='Prometheus host to connect to.',
    default=None)
parser.add_argument(
    '--config', type=str, default='config.json',
    help='Path to splitwise credentials.')
args = parser.parse_args()

registry = CollectorRegistry()
last_success_gauge = Gauge(
    'job_last_success_unixtime',
    'Last time a batch job successfully finished',
    registry=registry)
balance_gauge = Gauge(
    'balance',
    'Outstanding balance with friend',
    registry=registry,
    labelnames=['email', 'currency'])
gbp_balance_gauge = Gauge(
    'gbp_balance',
    'Outstanding balance with friend, in GBP',
    registry=registry,
    labelnames=['email'])


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


with open(args.config) as f:
    config = json.load(f)

sw = splitwise.Splitwise(
    config['OAuthConfig']['ConsumerKey'],
    config['OAuthConfig']['ConsumerSecret'])
sw.setAccessToken(
    {"oauth_token": config['Token']['Token'],
     "oauth_token_secret": config['Token']['TokenSecret']})


response = requests.get('https://api.exchangerate-api.com/v4/latest/GBP')
assert response.status_code == 200
data = response.json()
rates = data['rates']


for friend in sw.getFriends():
    if not friend.balances:
        continue
    gbp_balance = 0.0

    for balance in friend.balances:
        balance_gauge.labels(
            email=friend.email,
            currency=balance.currency_code).set(float(balance.amount))
        gbp_balance += float(balance.amount) / rates[balance.currency_code]

    gbp_balance_gauge.labels(email=friend.email).set(gbp_balance)


last_success_gauge.set_to_current_time()
if args.prometheus:
    push_to_gateway(args.prometheus, job='prometheus-splitwise-exporter',
                    registry=registry)
else:
    sys.stdout.buffer.write(generate_latest(registry=registry))
