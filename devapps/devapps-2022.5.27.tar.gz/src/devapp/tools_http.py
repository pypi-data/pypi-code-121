import requests, os
from devapp.app import tools, app, system, do


def download(url, to, chmod=None):
    fetch(url, to)
    if chmod:
        do(system, 'chmod %s "%s"' % (chmod, to))


def fetch(url, to):
    os.makedirs(os.path.dirname(to), exist_ok=True)

    if tools.exists(to):
        return app.info('exists already', file=to, store_log=True)

    app.info('Downloading', url=url, to=to)
    try:
        r = requests.get(url, stream=True)
    except Exception as ex:
        app.die('Cannot fetch', exc=ex)
    with open(to, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
        f.flush()
