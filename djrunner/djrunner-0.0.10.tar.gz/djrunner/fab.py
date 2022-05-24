
import os
import sys
import environ

from datetime import datetime
from fabric.api import env, run, local, sudo, cd, prefix, get, put
from contextlib import contextmanager


config = environ.Env()


@contextmanager
def source():
    with prefix('source ~/sites/{}/env/bin/activate'.format(config('DOMAIN'))):
        yield


def pull():
    run('git pull origin master')


def deploy():
    with cd('~/sites/{}/{}/'.format(config('DOMAIN'), config('PROJECT_NAME'))):
        pull()

        with source():
            run('pip install -r ./requirements.txt')
            run('python manage.py migrate')
            run('python manage.py collectstatic --noinput')
            run('python manage.py sync_translation_fields --noinput')

    restart()


def restart():
    project_name = config('PROJECT_NAME')

    with cd('~/sites/{}/{}/'.format(config('DOMAIN'), project_name)):
        pull()

    sudo('sudo supervisorctl restart {}'.format(config('PROJECT_NAME')))

    if config('CELERY') == 'on':
        sudo('sudo supervisorctl restart {}_celery'.format(project_name))
        sudo('sudo supervisorctl restart {}_celery_beat'.format(project_name))


def dump_db():
    file_path = '/home/dev/{}_{}.sql'.format(
        config('DB_NAME'),
        datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    )

    run('pg_dump {} > {}'.format(config('DB_NAME'), file_path))

    get(file_path, file_path)

    return file_path


def fetch_db():
    file_path = dump_db()

    local('sudo -u postgres psql -c "DROP DATABASE IF EXISTS {};"'.format(
        config('DB_NAME')
    ))

    local('sudo -u postgres psql -c "CREATE DATABASE {};"'.format(
        config('DB_NAME')
    ))

    local('sudo -u postgres psql -d {} -f {}'.format(
        config('DB_NAME'),
        file_path
    ))

    run('rm {}'.format(file_path))
    local('rm {}'.format(file_path))


def setup():
    frame = sys._getframe()
    env_file = os.path.join(
        os.path.dirname(frame.f_back.f_code.co_filename),
        '.env'
    )
    config.read_env(env_file)
    env.user = 'dev'
    env.hosts = [config('HOST')]
    env.password = config('HOST_PASSWORD')


def upload_env():

    put(  # TODO: fix basedir
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'),
        '/home/dev/sites/{}/{}/.env'.format(
            config('DOMAIN'), config('PROJECT_NAME'))
    )


def fetch_media():

    base_dir = os.path.dirname(os.path.abspath(__file__))

    local('rm -r -f {}'.format(os.path.join(base_dir, 'media')))

    local(
        'scp -r dev@{}:/home/dev/sites/{}/public/media {}'.format(
            config('HOST'), config('DOMAIN'), base_dir  # TODO: fix basedir
        )
    )
