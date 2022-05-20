import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
import yaml

from fiddler.core_objects import (
    DatasetInfo,
    DeploymentOptions,
    DeploymentType,
    ModelInfo,
)
from fiddler.fiddler_api import FiddlerApi
import logging

fiddler_core_version = '0.1.1'
LOG = logging.getLogger(__name__)


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def dockerfile(args):
    return f'''
    # syntax=docker/dockerfile:1
    FROM fiddlerai/fiddler-core:{fiddler_core_version}

    RUN mkdir -p /app/{args.org}/{args.project}/{args.model}

    COPY . /app/{args.org}/{args.project}/{args.model}

    RUN pip install -r /app/{args.org}/{args.project}/{args.model}/requirements.txt

    ENV FAR_MODEL_PATH {args.org}/{args.project}/{args.model}
    ENV SERVICE_RUN_MODE local

    CMD ["/bin/bash", "/app/runit.sh"]
    '''


def call_cmd(cmd, cwd):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        cwd=cwd,
    )

    return_code = None

    while True:
        output = process.stdout.readline()
        LOG.info(output.strip())
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            LOG.info(f'RETURN CODE: {return_code}')
            # Process has finished, read rest of the output
            for output in process.stdout.readlines():
                LOG.info(output.strip())
            for output in process.stderr.readlines():
                LOG.info(output.strip())
            break

    if return_code == 0:
        LOG.info('cmd successful')
    else:
        raise ValueError('cmd failed')


def build_cmd(args):
    LOG.info(f'building archive for  {args.org} {args.project} {args.model}')

    source = Path(args.source)
    if not source.is_dir():
        raise ValueError('source is not a directory')

    if not Path(source, 'requirements.txt').is_file():
        raise ValueError(f'requirements.txt not found in {source}')

    if args.train:
        if not Path(source, 'train.py').is_file():
            raise ValueError(f'train.py not found in {source}')
    else:
        if not Path(source, 'package.py').is_file():
            raise ValueError(f'package.py not found in {source}')
        if not Path(source, 'model.yaml').is_file():
            raise ValueError(f'model.yaml not found in {source}')
        if not Path(source, 'dataset.csv').is_file():
            raise ValueError(f'dataset.csv not found in {source}')
        if not Path(source, 'dataset.yaml').is_file():
            raise ValueError(f'dataset.yaml not found in {source}')

    with tempfile.TemporaryDirectory() as tmp:
        copytree(source, Path(tmp))
        docker_template = dockerfile(args)
        with open(tmp / Path('Dockerfile'), 'w') as output:
            output.write(docker_template)

        LOG.info(os.listdir(tmp))
        name = f'{args.org}-{args.project}-{args.model}'

        cmd = ['docker', 'build', '--file=Dockerfile', f'--tag={name}', '.']
        call_cmd(cmd, tmp)
        return 'done'


def run_cmd(args):
    name = f'{args.org}-{args.project}-{args.model}'

    cmd = [
        'docker',
        'run',
        '-d',
        '--rm',
        '--publish=5100:5100',
        f'--name={name}',
        f'{name}:latest',
    ]

    call_cmd(cmd, '.')


def register_cmd(args):
    client = FiddlerApi(args.endpoint, args.org, args.auth_key)
    if args.model in client.list_models(args.project):
        raise ValueError('model already exists in project')

    source = Path(args.source)
    if not source.is_dir():
        raise ValueError('source is not a directory')

    if not Path(source, 'model.yaml').is_file():
        raise ValueError(f'model.yaml not found in {source}')

    with open(Path(source, 'model.yaml')) as f:
        model_info = ModelInfo.from_dict(yaml.safe_load(f))

    with open(Path(source, 'dataset.yaml')) as f:
        dataset_info = DatasetInfo.from_dict(yaml.safe_load(f))

    if args.dataset:
        dataset_id = args.dataset
    else:
        dataset_id = f'{args.model}_dataset'

    try:
        dataset_info = client.get_dataset_info(args.project, dataset_id)
        LOG.info('Using existing dataset')
    except Exception as e:
        LOG.info(f'Dataset not found, uploading dataset {dataset_id}')
        with open(Path(source, 'dataset.csv')) as f:
            dataset_df = pd.read_csv(f)
            ds_dict = {'dataset': dataset_df}
            result = client.upload_dataset(
                project_id=args.project,
                dataset=ds_dict,
                dataset_id=dataset_id,
                info=dataset_info,
            )
            LOG.info(result)

    deployment_options = DeploymentOptions(
        deployment_type=DeploymentType.FAR,
        image=args.image,
        cpus=0.5,
        memory='512m',
    )

    result = client.register_model(
        args.project, args.model, dataset_id, model_info, deployment_options
    )

    LOG.info(result)
