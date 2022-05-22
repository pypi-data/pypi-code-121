import sys
import os
import logging
from server.common.variables import LOGGING_LEVEL, FORMATTER

sys.path.append('../../../messenger/')

# Создаем логгер - регистратор верхнего уровня с именем client
CLIENT_LOG = logging.getLogger('client')
# Установить уровень важности

# PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.getcwd()
PATH = os.path.join(os.path.split(PATH)[0], 'logs/client.log')

# Создаем обработчик, который выводит сообщения в поток stderr
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setLevel(logging.ERROR)

# Создать обработчик, который выводит сообщения в файл
FILE_HANDLER = logging.FileHandler(PATH, encoding='utf-8')

# подключаем объект Formatter к обработчикам
STREAM_HANDLER.setFormatter(FORMATTER)
FILE_HANDLER.setFormatter(FORMATTER)

# Добавляем обработчики к регистратору
CLIENT_LOG.addHandler(STREAM_HANDLER)
CLIENT_LOG.addHandler(FILE_HANDLER)
CLIENT_LOG.setLevel(LOGGING_LEVEL)

# Отладка
if __name__ == '__main__':
    CLIENT_LOG.critical('Критическая ошибка')
    CLIENT_LOG.error('Ошибка')
    CLIENT_LOG.warning('Предупреждение!')
    CLIENT_LOG.debug('Отладочная информация')
    CLIENT_LOG.info('Замечательный день для релиза!')
