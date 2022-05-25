import sys
import requests
import json
from pprint import pprint as pp

def init():
    sys.path.append('/Users/jakub/remote_code')
    from auth import credential_id, credential_secret, password
    return credential_id, credential_secret, password

def avail_fl_nodes(stats='all', gpu_count=1):
    credential_id, credential_secret, password = init()
    gpus = int(gpu_count or 1)
    filtering_call = f"https://worker.api.fluidstack.io/docker/nodes?bandwidth=1M&total_memory=1G&free_storage=10G&gpus={gpus}&cpu_cores=1"

    headers = {
        "X-Fluidstack-ID":  credential_id,
        "X-Fluidstack-Secret": credential_secret
    }

    api_response = requests.get(filtering_call, headers=headers).json()

    if stats=='all' or stats is None:
        import pandas as pd
        # pd.set_option('display.max_columns',  )
        df = pd.DataFrame.from_dict(api_response['nodes'])
        print(df.T)

    elif stats=='gpu':
        gpus = { x['id']:x['gpus'] for x in api_response['nodes'] }
        pp(gpus)

    else:
        raise NotImplementedError('Choose one of {gpu, all}')


def start_docker(target_id: str):
    credential_id, credential_secret, password = init()
    # example target_id = 'cc8bd5fe-07fd-5ea7-b88b-05bf10c57c7c'

    post_url = 'https://worker.api.fluidstack.io/docker/containers'

    headers = {
        "X-Fluidstack-ID":  credential_id,
        "X-Fluidstack-Secret": credential_secret,
        "Content-Type": "application/json"
    }

    # data = '{"node_id":"{target_id}", "image":"sickp/alpine-sshd:latest"}'
    data = {"node_id" : target_id, "image": "ufoym/deepo:latest"}

    reply = requests.post(post_url, headers=headers, data=data)
    print(reply)


def show_running():
    credential_id, credential_secret, password = init()

    headers = {
        "X-Fluidstack-ID":  credential_id,
        "X-Fluidstack-Secret": credential_secret,
        "Content-Type": "application/json"
    }

    req_url = "https://worker.api.fluidstack.io/docker/containers?status=running"

    reply = requests.get(req_url, headers=headers).json()
    pp(reply)

def stop_container(container_id: str):
    credential_id, credential_secret, password = init()

    headers = {
        "X-Fluidstack-ID":  credential_id,
        "X-Fluidstack-Secret": credential_secret
    }

    req_url = 'https://worker.api.fluidstack.io/docker/containers/{container_id}/stop'

    try:
        reply = requests.post(req_url, headers=headers).json()
        pp(reply)
    except json.decoder.JSONDecodeError:
        reply = requests.post(req_url, headers=headers).content
        print(f"JSONDecodeERROR: {reply}")


def start_container(node_id: str):
    credential_id, credential_secret, password = init()

    # login
    login_url = "https://auth.api.fluidstack.io/client/login"
    data = {"email": "james.langr@gmail.com", "password": password}

    reply = requests.post(login_url, data=data)
    token = reply.json()['token']

    creation_headers = {
        "X-Fluidstack-ID":  credential_id,
        "X-Fluidstack-Secret": credential_secret,
        "Content-Type": "application/json"
    }

    # Create
    creation_url = "https://worker.api.fluidstack.io/docker/containers"

    with open('/Users/jakub/.ssh/id_rsa.pub') as f:
        ssh_key = f.read()
    data = {"node_id": node_id, "image": "fluidstackio/pytorch",
            "ports": ["22/tcp", "8888/tcp", "6006/tcp"],
            "gpus": "all", "ssh_key": ssh_key}
    headers = f"Authorization: Bearer {token}"
    data =  json.dumps(data).encode("utf-8")
    confirmation = requests.post(creation_url, data=data,
                                 headers=creation_headers)

    print(confirmation.json())