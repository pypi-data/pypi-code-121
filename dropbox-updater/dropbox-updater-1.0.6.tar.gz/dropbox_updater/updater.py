import hashlib
import json
import os
import shutil
import sys
import tarfile
import time
from copy import deepcopy
from glob import glob
from threading import Thread

import requests
from requests_futures.sessions import FuturesSession

from .logger import logger

META_DATA_URL = 'https://api.dropboxapi.com/2/files/get_metadata'
DOWNLOAD_URL = 'https://content.dropboxapi.com/2/files/download'
UPLOAD_URL = 'https://content.dropboxapi.com/2/files/upload'
DROPBOX_HASH_CHUNK_SIZE = 4 * 1024 * 1024


def compress(file_path, dir_path, excluded):
    logger.info(f'Compressing to {file_path}...')
    file_dir_path = os.path.dirname(file_path)
    if file_dir_path:
        os.makedirs(file_dir_path, exist_ok=True)
    excluded = excluded + ['dist', 'venv', file_path]
    with tarfile.open(file_path, 'w:bz2') as tar:
        for name in glob(os.path.join(dir_path, '*')):
            basename = os.path.basename(name)
            if basename in excluded:
                continue
            tar.add(name, arcname=basename)


def remove_old_files(extract_dir, excluded):
    for name in glob(os.path.join(extract_dir, '*')):
        basename = os.path.basename(name)
        if basename in excluded + ['dist', 'venv']:
            continue
        if os.path.isfile(name) or os.path.islink(name):
            os.unlink(name)
        elif os.path.isdir(name):
            shutil.rmtree(name)


def extract(dropbox_path, file_path, extract_dir):
    os.makedirs(extract_dir, exist_ok=True)
    if dropbox_path.endswith('tar.gz'):
        tar = tarfile.open(file_path, 'r:gz')
        tar.extractall(extract_dir)
        tar.close()
    elif dropbox_path.endswith('tar.bz2'):
        tar = tarfile.open(file_path, 'r:bz2')
        tar.extractall(extract_dir)
        tar.close()
    elif dropbox_path.endswith('tar'):
        tar = tarfile.open(file_path, 'r:')
        tar.extractall(extract_dir)
        tar.close()


def post_cloud_hash(session, data):
    token = data['token']
    body = {'path': data['dropbox_path']}
    headers = {'Authorization': f'Bearer {token}'}
    data['meta_data'] = session.post(META_DATA_URL, headers=headers, json=body, timeout=30)
    return data


def get_local_hash(file_path):
    try:
        with open(file_path, 'rb') as f:
            block_hashes = b''
            while True:
                chunk = f.read(DROPBOX_HASH_CHUNK_SIZE)
                if not chunk:
                    break
                block_hashes += hashlib.sha256(chunk).digest()
            return hashlib.sha256(block_hashes).hexdigest()
    except OSError:
        return None


def get_cloud_hash(data):
    try:
        response = data['meta_data'].result()
        if response.ok:
            return response.json()['content_hash']
        return None
    except requests.exceptions.RequestException:
        return None


def update_hash(data):
    data['cloud_hash'] = get_cloud_hash(data)
    data['local_hash'] = get_local_hash(data['file_path'])
    data['hash_match'] = data['cloud_hash'] == data['local_hash']
    return data


def post_download(session, data):
    token = data['token']
    body = {'path': data['dropbox_path']}
    headers = {
        'Dropbox-API-Arg': json.dumps(body),
        'Authorization': f'Bearer {token}',
    }
    data['file'] = session.get(DOWNLOAD_URL, headers=headers, stream=True, timeout=60)
    return data


def post_upload(session, data):
    token = data['token']
    dropbox_path = data['dropbox_path']
    logger.info(f'Uploading to {dropbox_path}...')
    body = {'path': dropbox_path, 'mode': 'overwrite'}
    headers = {
        'Dropbox-API-Arg': json.dumps(body),
        'Content-Type': 'application/octet-stream',
        'Authorization': f'Bearer {token}',
    }
    fp = open(data['file_path'], 'rb')
    data['upload'] = session.post(UPLOAD_URL, data=fp, headers=headers, timeout=30)
    return data


def write_file(i, total, data):
    try:
        logger.info(f'Downloading ({i}/{total})...')
        response = data['file'].result()
        if not response.ok:
            logger.error('Download failed.')
            return data
        dir_path = os.path.dirname(data['file_path'])
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(data['file_path'], 'wb') as f:
            f.write(response.content)
        return data
    except requests.exceptions.RequestException:
        return data


def check_for_updates(data, restart=True):
    logger.info('Checking for updates...')
    data = deepcopy(data)
    session = FuturesSession()
    data = [post_cloud_hash(session, d) for d in data]
    data = [update_hash(d) for d in data]
    update_required = [d for d in data if not d['hash_match']]
    if update_required == []:
        logger.info('Already upto date.')
        return
    names = ', '.join(d['name'] for d in update_required)
    logger.info(f'{names} has new updates.')
    update_required = [post_download(session, d) for d in update_required]
    total = len(update_required)
    update_required = [write_file(i, total, d) for i, d in enumerate(update_required)]
    logger.info(f'Downloading ({total}/{total})...')
    for i, data in enumerate(update_required):
        logger.info(f'Extracting ({i}/{total})...')
        remove_old_files(data['extract_dir'], data['exclude'])
        extract(data['dropbox_path'], data['file_path'], data['extract_dir'])
    logger.info(f'Extracting ({total}/{total})...')
    if restart:
        os.execl(sys.executable, sys.executable, *sys.argv)


def check_for_updates_task(data, restart=True, interval=1500, delay_first=1500):
    time.sleep(delay_first)
    while True:
        try:
            check_for_updates(data, restart=restart)
        except Exception as exp:
            logger.error(f'Unhandled exception in updater: {exp}')
        time.sleep(interval)


def start_check_for_updates_task(data, restart=True, interval=1500, delay_first=1500):
    '''Periodically updates the bot in a thread'''
    args = data, restart, interval, delay_first
    Thread(target=check_for_updates_task, args=args, daemon=True).start()


def upload(data):
    data = deepcopy(data)
    for datum in data:
        old_hash = get_local_hash(datum['file_path'])
        compress(datum['file_path'], datum['extract_dir'], datum['exclude'])
        datum['hash_match'] = old_hash == get_local_hash(datum['file_path'])
    update_required = [d for d in data if not d['hash_match']]
    if update_required == []:
        logger.info('Already upto date.')
        return
    session = FuturesSession()
    names = ', '.join(d['name'] for d in update_required)
    logger.info(f'{names} requires uploading.')
    total = len(update_required)
    update_required = [post_upload(session, d) for d in update_required]
    for i, data in enumerate(update_required):
        try:
            logger.info(f'Uploading ({i}/{total})...')
            response = data['upload'].result()
            if not response.ok:
                logger.error('Upload failed.')
        except requests.exceptions.RequestException:
            logger.error('Upload failed.')
    logger.info(f'Uploading ({total}/{total})...')
