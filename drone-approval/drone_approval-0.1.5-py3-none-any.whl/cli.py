# pylint: disable=unexpected-keyword-arg
import os
import json
import logging
from typing import Optional, List, Dict

import click
import httpx

logger = logging.getLogger(__name__)
        
@click.command()
@click.option("-t","--token",required=True)
@click.option("-b","--base-url",required=True)
@click.option("-r","--repo",required=True,default=os.environ.get('DRONE_REPO'))
@click.option("-c","--build",type=int,required=True,default=os.environ.get('DRONE_BUILD_NUMBER'))
@click.option("-n","--name",required=True,default=os.environ.get('DRONE_DEPLOY_TO'))
@click.option("-s","--stage",type=int,required=True,default=os.environ.get('DRONE_STAGE_NUMBER'))
@click.option("-i","--step",type=int,required=True,default=os.environ.get('DRONE_STEP_NUMBER'))
@click.option("-g","--reviewers",required=True)
@click.option("-a","--created-by",required=False)
def check_approval(
        token:str,
        base_url:str,
        repo:str,
        build:int,
        name:str,
        stage:int,
        step:int,
        reviewers:str,
        created_by:str,
    ):
    if reviewers.startswith('@'):
        with open(reviewers[1:],'r') as groupsfile:
            groups = json.loads(groupsfile.read())
    else:
        groups = []
        for group_def in reviewers.split(','):
            parts = group_def.split(':')
            group_name = parts[0]
            users = parts[1:]
            groups.append({'name':group_name,'users':users})
    res = httpx.get(
        f"{base_url}/api/v1/approval-result",
        params={'build':build,'repo':repo},
        headers={"Authorization": f"Bearer {token}"},
    )
    if res.status_code == 204:
        msg = {
                'name':name,
                'repo':repo,
                'build':build,
                'stage':stage,
                'step':step,
                'groups':groups,
            }
        res = httpx.post(
            f"{base_url}/api/v1/approval-requests",
            headers={"Authorization": f"Bearer {token}"},
            json=msg,
        )
        if res.status_code != 200:
            logger.error('Failed creating an approval request with %s',res.json())
        else:
            print('Created approval request',res.text)
            res_data = res.json()
            print(json.dumps(res_data,indent=4))
        raise click.Abort("Before going on we need the approval")
    elif res.status_code == 200:
        approval_request = res.json()
        if approval_request['approved']:
            print('Great we have an approval, let\'s roll.')
            print(json.dumps(approval_request,indent=4))
    else:
        raise click.ClickException(f'Failed fetching the approval status with {res.status_code}')



def main():
    check_approval(auto_envvar_prefix='PLUGIN')

if __name__ == '__main__':
    main()
