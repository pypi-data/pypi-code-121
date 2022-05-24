""" Core module with cli """
import click
import json
import os
import requests
from datetime import datetime, timedelta
from dynatrace import Dynatrace
from dynatrace import TOO_MANY_REQUESTS_WAIT
from dynatrace.environment_v2.tokens_api import SCOPE_METRICS_READ, SCOPE_METRICS_INGEST
from termcolor import cprint
from pprint import pprint
from requests.api import get, head
from urllib3.exceptions import InsecureRequestWarning
# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
# Set `verify=False` on `requests.post`.
# requests.post(url='https://example.com', data={'bar':'baz'}, verify=False)



@click.group()
def main():
    """
    dt_log_send is a cli for sending logs to Dynatrace\n
    Set the following environment variables\n
    DT_API_KEY = 'API-YOURAPIKEY'\n
    DT_SERVER_URI = 'https://activegate.example.com:9999/e/tenant_id'

    Example Usage: dt_log_send CRCO8GWSFTP01 "ERROR: SMB VERIFICATION FAILED"
    """

@main.command('check-env', short_help='Check required environment variables')
def check_env():
    """ Prints out the current necessary environment variables """
    dt_api_key = os.getenv('DT_API_KEY')
    dt_server_uri = os.getenv('DT_SERVER_URI')
    print(f"Your environment has {dt_api_key} for the variable DT_API_KEY")
    print(f"Your environment has {dt_server_uri} for the variable DT_SERVER_URI")


@main.command('get-hosts', short_help='Get all hosts with some properties')
def get_hosts():
    dt_api_key = os.getenv('DT_API_KEY')
    dt_server_uri = os.getenv('DT_SERVER_URI')
    dt = Dynatrace(dt_server_uri, dt_api_key)
    for entity in dt.entities.list('type("HOST")', fields="properties.memoryTotal,properties.monitoringMode"):
        print(entity.entity_id, entity.display_name, entity.properties)

@main.command('get-hosts-idle-cpu', short_help='Get idle CPU for all hosts')
def get_hosts_idle_cpu():
    dt_api_key = os.getenv('DT_API_KEY')
    dt_server_uri = os.getenv('DT_SERVER_URI')
    dt = Dynatrace(dt_server_uri, dt_api_key)
    for metric in dt.metrics.query("builtin:host.cpu.idle", resolution="Inf"):
        print(metric)

@main.command('create-token', short_help='Create a new API token that can read and ingest metrics')
def get_hosts_idle_cpu():
    dt_api_key = os.getenv('DT_API_KEY')
    dt_server_uri = os.getenv('DT_SERVER_URI')
    dt = Dynatrace(dt_server_uri, dt_api_key)
    for metric in dt.metrics.query("builtin:host.cpu.idle", resolution="Inf"):
        print(metric)

@main.command('send-log', short_help='Upload a log entry to Dynatrace')
@click.argument("hostname")
@click.argument("log-level")
@click.argument("log-entry")
def send_log(hostname, log_level, log_entry):
    dt_api_key = os.getenv('DT_API_KEY')
    dt_server_uri = os.getenv('DT_SERVER_URI')
    dt = Dynatrace(dt_server_uri, dt_api_key)
    log_event = { "host.name": hostname, "status": log_level, "content": log_entry }
    resp = dt.logs.ingest(log_event)
    print(resp)

