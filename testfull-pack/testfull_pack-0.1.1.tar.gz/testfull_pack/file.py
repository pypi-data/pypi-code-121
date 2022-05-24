from os import environ
from os import remove
from os.path import abspath
from os.path import exists
from pprint import pprint
from re import sub
from typing import Optional

from logsmal import logger

from basehash import BaseHash


def verify_authenticity_of_file(infile: str, hash_sum: str):
    return BaseHash.check_hash_sum(BaseHash.file(infile), hash_sum)


def verify_authenticity_text(text: str, hash_sum: str):
    return BaseHash.check_hash_sum(BaseHash.text(text), hash_sum)


class TextFile:
    """
    Вернуть файл если хеш сумма верна
    """

    def __init__(self, path: str, hash_sum: Optional[str]):
        """
        Проверить подлинность файла

        :param path:
        :param hash_sum:
        """
        if hash_sum is not None:
            verify_authenticity_of_file(path, hash_sum)
        self.path = path
        self.full_path = abspath(self.path)

    def read(self):
        with open(self.full_path, "r", encoding='utf-8') as _f:
            return _f.read()

    def update(self, text: str):
        with open(self.full_path, "w", encoding='utf-8') as _f:
            return _f.write(text)


class ReadTextFile(TextFile):
    """
    Вернуть данные из фала если хеш сумма верна
    """

    def __init__(self, path: str, hash_sum: Optional[str]):
        """
        Проверить подлинность файла

        :param path:
        :param hash_sum:
        """
        super().__init__(path, hash_sum)
        self.__текст = None

    @property
    def текст(self):
        # Записать данные в переменную из файла, только при первом обращении.
        if self.__текст is None:
            return self.read()
        return self.__текст


class RollingFile(ReadTextFile):
    """
    Файл с возможностью отката данных, на момент создания класса.
    Или удалить файл, если он не был создан, на момент создания класса.


    with RollingFile():
        ...
    """

    def __init__(self, path: str, hash_sum: Optional[str]):
        super().__init__(path, hash_sum)
        self.существование = exists(self.full_path)
        # Если файл не существовал, то удаляем его при откате
        if not self.существование:
            self.прошлые_данные_из_файла = ''
        else:
            self.прошлые_данные_из_файла: str = self.текст

    def rolling(self):
        if self.существование:
            with open(self.full_path, 'w', encoding='utf-8') as _f:
                _f.write(self.прошлые_данные_из_файла)
        else:
            remove(self.full_path)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.rolling()


def readAndSetEnv(*path_files: str):
    """
    Чтение переменных окружения из указанного файла,
    и добавление их в ПО `python`
    """
    for _path_file in path_files:
        if exists(_path_file):
            with open(_path_file, 'r', encoding='utf-8') as _file:
                res = {}
                for line in _file:
                    tmp = sub(r'^#[\s\w\d\W\t]*|[\t\s]', '', line)
                    if tmp:
                        k, v = tmp.split('=', 1)
                        # Если значение заключено в двойные кавычки, то нужно эти кавычки убрать
                        if v.startswith('"') and v.endswith('"'):
                            v = v[1:-1]

                        res[k] = v
            environ.update(res)
            pprint(res)
        else:
            logger.warning(f"No search file {_path_file}")
