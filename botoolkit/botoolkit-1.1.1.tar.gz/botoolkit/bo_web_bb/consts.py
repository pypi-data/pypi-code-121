from copy import (
    copy,
)


RUN_WEB_BB_APP_CONTAINER_COMMANDS = [
    'dockerize -template /srv/tmp/app_requirements_ssh.txt.tmpl:/srv/tmp/app_requirements_ssh.txt',
    'pip3 install --no-cache-dir -r /srv/tmp/app_requirements_ssh.txt',
    'dockerize -template /srv/tmp/app.conf.tmpl:/srv/tmp/app.conf',
    'export WEB_BB_CONF=/srv/tmp/app.conf DJANGO_SETTINGS_MODULE=web_bb_app.settings PYTHONPATH=$PYTHONPATH:/srv/web_bb_app/src',
    'python3 /srv/web_bb_app/src/web_bb_app/manage.py migrate --force',
    'python3 /srv/web_bb_app/src/web_bb_app/manage.py migrate --force',
]

DATABASER_RUN_WEB_BB_APP_CONTAINER_COMMANDS = [
    *RUN_WEB_BB_APP_CONTAINER_COMMANDS,
    'python3 /srv/web_bb_app/src/web_bb_app/manage.py add_generic_tables',
    'python3 /srv/web_bb_app/src/web_bb_app/manage.py create_default_date_range_partition',
]


RUN_ETALON_WEB_BB_APP_CONTAINER_COMMANDS = [
    *RUN_WEB_BB_APP_CONTAINER_COMMANDS,
    'python3 /srv/web_bb_app/src/web_bb_app/manage.py load_etalon_fixtures',
]
