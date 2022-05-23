import streamlit as st

from .api.client import ApiClient
from .authentication import get_jwt_from_browser
from .interactors import Job, Run


def get_api_client(st_element: st = st) -> ApiClient:
    client = ApiClient()
    client.jwt_token = get_jwt_from_browser()
    if client.jwt_token is None:
        client.api_token = st_element.text_input(
            'Enter Pollination APIKEY', type='password',
            help=':bulb: You only need an API Key to access private projects. '
            'If you do not have a key already go to the settings tab under your profile to '
            'generate one.'
        )
    return client


def job_selector(
    client: ApiClient, label: str = 'Job URL',
    default: str = None, help: str = None
) -> Job:
    job_url = st.text_input(label=label, value=default, help=help)
    if not job_url or job_url == 'None':
        return None

    url_split = job_url.split('/')
    job_id = url_split[-1]
    project = url_split[-3]
    owner = url_split[-5]

    return Job(owner, project, job_id, client)


def run_selector(
    client: ApiClient, label: str = 'Run URL',
    default: str = None, help: str = None
) -> Run:
    run_url = st.text_input(label=label, value=default, help=help)
    if not run_url or run_url == 'None':
        return None

    url_split = run_url.split('/')
    run_id = url_split[-1]
    job_id = url_split[-3]
    project = url_split[-5]
    owner = url_split[-7]

    return Run(owner, project, job_id, run_id, client)
