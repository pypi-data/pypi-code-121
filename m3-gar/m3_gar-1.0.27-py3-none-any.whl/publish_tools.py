import datetime
import fileinput
import io
import os
from io import (
    BytesIO,
)
from shutil import (
    rmtree,
)
from zipfile import (
    BadZipfile,
    ZipFile,
)

import requests
from django.conf import (
    settings,
)
from git import (
    Repo,
)
from setuptools import (
    setup,
)
from twine.commands.upload import (
    main,
)

from m3_gar.exceptions import (
    PublisherError,
)
from setup_kwargs import (
    make_setup_kwargs,
)


class GARSchemaManager:
    """
    Базовый класс, отвечающий за получение схем ГАР
    """

    def __init__(self, repo):
        self.repo = repo

        self.downloaded_schemas = []
        self.existing_schemas = os.listdir(settings.GAR_SCHEMAS_FOLDER)

    def process_schemas(self):
        """
        Скачивание схем с удаленного адреса
        """
        try:
            zip_archive = self._retrieve_schemas()
        except BadZipfile as e:
            raise PublisherError('Некорректный архив! {}'.format(str(e)))
        else:
            # сохраняем новые схемы с заменой
            self._save_schema(zip_archive)

    def has_schema_changes(self):
        """
        Проверяет, были ли изменения в файлах схем
        """
        # сначала добавим все файлы в репу - может, что-то пришло новое и удалилось старое
        index = self.repo.index
        index.add([
            str(settings.GAR_SCHEMAS_FOLDER / file_name)
            for file_name in os.listdir(settings.GAR_SCHEMAS_FOLDER)
        ])

        # смотрим, были ли изменения
        return bool(index.diff('HEAD'))

    def _retrieve_schemas(self):
        """
        Общий метод получения схем
        """
        raise NotImplementedError()

    def _lower_ext(self, file_name):
        """
        Отдает наименование файла с расширением в нижнем регистре
        """
        file_path, ext = os.path.splitext(file_name)
        return ''.join((file_path, ext.lower()))

    def _get_download_path(self, file_name):
        """
        Возвращает путь до файла в каталоге схем
        """
        # для консистентности всегда будем сохранять с расширением в нижнем регистре
        file_name = self._lower_ext(file_name)

        return settings.GAR_SCHEMAS_FOLDER / file_name

    def _save_schema(self, zip_archive):
        """
        Распаковывает архив и сохраняет файлы схемы
        """
        for file_name in zip_archive.namelist():
            if not self._validate_file_in_zip(file_name):
                continue

            table_name_from_xsd = self._get_table_from_xsd(file_name)
            self._delete_schema_if_found(table_name_from_xsd)

            xsd_file = zip_archive.read(file_name)
            with open(self._get_download_path(file_name), 'w+b') as write_file:
                write_file.write(xsd_file)
                self.downloaded_schemas.append(write_file.name)

    def _validate_file_in_zip(self, file_name):
        """
        Проверка, нужно ли обрабатывать файл
        """
        return True

    def _get_table_from_xsd(self, file_name):
        """
        Возвращает название таблицы из имени файла
        """
        split_file_name = file_name.split('_')
        table_name = '_'.join(split_file_name[:-6])

        return f'{table_name}_'

    def _delete_schema_if_found(self, table_name_from_xsd):
        """
        Удаление схемы из папки со схемами, если название таблицы было найдено
        в имени файла
        """
        for existing_schema in self.existing_schemas:
            if self._get_table_from_xsd(existing_schema) == table_name_from_xsd:
                file_path = settings.GAR_SCHEMAS_FOLDER / existing_schema
                os.remove(file_path)


class DownloadGARSchemaManager(GARSchemaManager):
    """
    Класс, который обеспечивает скачивание схем ГАР с указанного url
    """

    def __init__(self, url, repo, timeout=30):
        self.url = url
        self.timeout = timeout

        super().__init__(repo)

    def _retrieve_schemas(self):
        """
        Скачивание архива со схемами
        """
        response = requests.get(self.url, stream=True, timeout=self.timeout)

        return ZipFile(BytesIO(response.content))


class ArchiveGARSchemaManager(GARSchemaManager):
    """
    Класс, который обеспечивает обработку схем ГАР из уже скачанного архива
    """

    def __init__(self, path, repo):
        self.path = path

        super().__init__(repo)

    def _retrieve_schemas(self):
        """
        Отдает объект ZipFile по указанному пути
        """
        return ZipFile(self.path)

    def _get_download_path(self, file_name):
        file_name = self._lower_ext(file_name)

        return os.path.join(settings.GAR_SCHEMAS_FOLDER, file_name.split('/')[1])

    def _validate_file_in_zip(self, file_name):
        return file_name.startswith('Schemas')

    def _get_table_from_xsd(self, file_name):
        file_name = file_name.split('/')[1]

        return super()._get_table_from_xsd(file_name)


class RepoManager:
    """
    Класс для работы с репозиторием при релизе новой версии пакета
    """

    def __init__(self, test_mode=False):
        self.repo = Repo(settings.GAR_BASE_DIR.parent)
        self.test_mode = test_mode

    def index_add(self):
        """
        Добавляет новые файлы в репозиторий для последующего коммита
        """
        # файлы схем уже добавлены, добавляем миграции
        files_to_add = []
        migrations_dir = settings.GAR_BASE_DIR / 'migrations'
        for file_name in os.listdir(migrations_dir):
            if file_name.endswith('.pyc'):
                continue

            files_to_add.append(migrations_dir / file_name)

        self.repo.index.add(map(str, files_to_add))

    def save_changes(self, new_version):
        """
        Сохраняет изменения в пакете путем коммита и пуша
        """
        push_args = []

        if self.test_mode:
            # в этом случае создадим новую ветку по названию версии
            # и закоммитим туда, а не в мастер
            new_branch_name = f'test-patch-{new_version}'
            new_branch = self.repo.create_head(new_branch_name)
            new_branch.checkout()

            push_args.append('--set-upstream')

        push_args.extend([self.repo.remote(), self.repo.head.ref])

        self.repo.git.commit(
            '-a',
            '-m',
            f'Автогенерация патча {new_version} по обновлению формата ГАР',
        )
        self.repo.git.push(*push_args)


class ReleasePreparer:
    """
    Класс, ответственный за подготовку к выпуску.
    Повышает версию пакета и дополняет чейнжлог автосгенерированной фразой
    """

    def __init__(self):
        self.version_file = str(settings.GAR_BASE_DIR / 'version.py')
        self.changelog_file = str(settings.GAR_BASE_DIR.parent / 'CHANGELOG.rst')
        self.new_version_str = ''

    def prepare(self):
        """
        Основной метод класса подготовки
        """
        self._update_version()
        self._update_changelog()

    def _update_version(self):
        """
        Увеличивает последнюю цифру в файле версии
        """
        with fileinput.input(self.version_file, inplace=True) as version_file:
            for line in version_file:
                if line.startswith('VERSION = '):
                    version_str = line.split('=')[1].strip()[1:-1]
                    major, minor, patch = map(int, version_str.split(','))
                    next_patch = patch + 1

                    self.new_version_str = f'{major}.{minor}.{next_patch}'

                    print(f'VERSION = ({major}, {minor}, {next_patch})')

                else:
                    print(line.strip('\n'))

    def _update_changelog(self):
        """
        Создает новую запись в чейнжлоге о текущей версии
        """
        if not self.new_version_str:
            return

        today = datetime.date.today()
        today_str = today.strftime('%Y.%m.%d')
        log_entry_text = (
            f'**{self.new_version_str}**\n'
            f'- Автогенерируемый патч по обновлению формата ГАР ({today_str})\n'
        )

        with io.open(self.changelog_file, 'r+', encoding='utf-8') as changelog_file:
            content = changelog_file.read()

        content = content.split('\n', 2)
        content.insert(-1, log_entry_text)
        content = '\n'.join(content)

        with io.open(self.changelog_file, 'w', encoding='utf-8') as changelog_file:
            changelog_file.seek(0, 0)
            changelog_file.write(content)


class Releaser:
    """
    Класс, отвечающий за создание и выпуск пакета
    """

    def __init__(self, new_version, test_mode=False):
        self.new_version = new_version
        self.test_mode = test_mode

    def release(self):
        """
        Основной метод запуска сборки
        """
        self._build_dist()

        try:
            self._publish()
        finally:
            self._clear_build_folder()

    def _build_dist(self):
        """
        Создание пакета
        """
        cwd = os.getcwd()
        os.chdir(settings.GAR_BASE_DIR.parent)

        try:
            new_setup_kwargs = make_setup_kwargs()
            new_setup_kwargs.update({
                'version': self.new_version,
                'script_name': 'setup.py',
                'script_args': ['sdist', 'bdist_wheel'],
            })
            setup(**new_setup_kwargs)
        finally:
            os.chdir(cwd)

    def _clear_build_folder(self):
        """
        Очистка после билда пакета
        """
        rmtree(settings.GAR_BASE_DIR.parent / 'build')
        rmtree(settings.GAR_BASE_DIR.parent / 'dist')

    def _publish(self):
        """
        Загрузка пакета на pypi
        Для получения логина-пароля используется файл ~/.pypirc, там должен
        быть указан адрес до pypi под категорией pypi,
        и адрес до тестового pypi под категорией testpypi, если нужно
        использовать тестовый режим скрипта
        """
        pypirc_config = ['-r', 'pypi']
        if self.test_mode:
            pypirc_config = ['-r', 'testpypi']

        args = pypirc_config + ['dist/*']

        cwd = os.getcwd()
        os.chdir(settings.GAR_BASE_DIR.parent)

        try:
            main(args)
        finally:
            os.chdir(cwd)
