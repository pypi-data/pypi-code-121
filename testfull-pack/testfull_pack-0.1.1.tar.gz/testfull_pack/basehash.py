from hashlib import sha256


class BaseHash:

    @staticmethod
    def file(path_file: str):
        """
        Получить хеш сумму данных в файле, по его пути

        :param path_file: Путь к файлу
        """
        h = sha256()
        b = bytearray(128 * 1024)
        mv = memoryview(b)
        with open(path_file, 'rb', buffering=0) as f:
            for n in iter(lambda: f.readinto(mv), 0):
                h.update(mv[:n])
        return h.hexdigest()

    @staticmethod
    def text(text: str) -> str:
        """
        Получить хеш сумму текста
        """
        return sha256(text.encode()).hexdigest()

    @staticmethod
    def check_hash_sum(unknown_hash_sum: str, true_hash_sum: str):
        """
        Сравить хеш суммы

        :param unknown_hash_sum: Полученная(неизвестная) хеш сумма
        :param true_hash_sum: Требуемая хеш сумма
        """
        if unknown_hash_sum != true_hash_sum:
            raise ValueError(f"{unknown_hash_sum} != {true_hash_sum}")
        return True
