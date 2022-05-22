class ConfigurationFormatEnum:
    """
    Форматы результирующего конфигурационного файла
    """
    CONF = 'conf'
    ENV = 'env'

    values = {
        CONF: 'configuration with conf format',
        ENV: 'configuration with env format with environment variables',
    }

    def __repr__(self):
        formats = '\n'.join(
            [
                f'{extension} - {description}'
                for extension, description in self.values.items()
            ]
        )

        result = f'format configuration file. Allowed formats:\n{formats}'

        return result

    def __str__(self):
        return self.__repr__()


class MemoryDimensionEnum:
    """
    Единицы измерения памяти
    """
    MB = 'MB'
    GB = 'GB'
    KB = 'kB'

    values = {
        MB: 'Megabyte',
        GB: 'Gigabyte',
        KB: 'Kilobyte',
    }

    @classmethod
    def ends_with_dimension(
        cls,
        value: str,
    ):
        """
        Проверка окончания строки единицей измерения
        """
        return (
            value.endswith(cls.MB) or
            value.endswith(cls.GB) or
            value.endswith(cls.KB)
        )
