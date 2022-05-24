import os
import requests
from requests_toolbelt.multipart import (
    encoder,
)
from django.core.management import (
    BaseCommand,
)


class Command(BaseCommand):
    help = 'Команда публикации дампа БД в хранилище. В переменной окружение AUTH_TOKEN ожидается токен OAuth.'
    usage_str = (
        'Usage: python manage.py gar_upload_dump '
        '--path=<path_to_dump> '
        '--store_url=<url_of_store>'
        '--upload_path=<path_in_store_to_upload>'
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--path',
            action='store',
            dest='path',
            help='Путь до файла c дампом',
            default='/home/app/web/dumps/m3_gar_dump.back',
        )
        parser.add_argument(
            '--store_url',
            action='store',
            dest='store_url',
            help='Адрес хранилища',
            default='https://cloud-api.yandex.net/v1/disk/resources',
        )
        parser.add_argument(
            '--upload_path',
            action='store',
            dest='upload_path',
            help='Путь в хранилище, кудо нужно разместить файл',
            default='gar/m3_gar_dump.back',
        )

    def handle(self, path, store_url, upload_path, **options):
        token = os.getenv('AUTH_TOKEN')
        headers = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {token}',
        }
        res = requests.get(f'{store_url}/upload?path={upload_path}&overwrite=true', headers=headers).json()

        with open(path, 'rb') as f:
            data = encoder.MultipartEncoder({'file': f})
            headers['Content-Type'] = data.content_type
            try:
                requests.put(res['href'], data=data)
            except KeyError:
                print(res)
