"""Программа-сервер"""
import argparse
import configparser
import os
import sys
import logging
import threading

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from common.decorators import log
from common.variables import DEFAULT_PORT
from server_dir.core import MessageProcessor
from server_dir.server_database import ServerStorage
from server_dir.main_window import MainWindow

# Инициализация логирования сервера.
logger = logging.getLogger('server')

# Флаг, что был подключён новый пользователь, нужен чтобы не мучить BD
# постоянными запросами на обновление
new_connection = False
connection_locker = threading.Lock()


@log
def create_arg_parser(default_port, default_address):
    """Парсер аргументов командной строки."""
    logger.debug(
        f'Инициализация парсера аргументов командной строки: {sys.argv}')
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    parser.add_argument('--no_gui', action='store_true')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    gui_flag = namespace.no_gui
    logger.debug('Аргументы успешно загружены.')
    return listen_address, listen_port, gui_flag


@log
def config_load():
    """Парсер конфигурационного ini файла."""
    config = configparser.ConfigParser()
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.getcwd()
    sys.path.insert(0, f'{dir_path}/common')
    config.read(f"{dir_path}/{'server.ini'}")
    # Если конфиг файл загружен правильно, запускаемся, иначе конфиг по
    # умолчанию.
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config


@log
def main():
    """Основная функция"""
    # Загрузка файла конфигурации сервера
    config = config_load()

    # Загрузка параметров командной строки, если нет параметров, то задаём
    # значения по умолчанию.
    listen_address, listen_port, gui_flag = create_arg_parser(
        config['SETTINGS']['Default_port'],
        config['SETTINGS']['Listen_Address'])

    # Инициализация базы данных
    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    # Создание экземпляра класса - сервера и его запуск:
    server = MessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Если указан параметр без GUI, то запускаем простенький обработчик
    # консольного ввода
    if gui_flag:
        while True:
            command = input('Введите exit для завершения работы сервера.')
            if command == 'exit':
                # Если выход, то завершаем основной цикл сервера.
                server.running = False
                server.join()
                break

    # Если не указан запуск без GUI, то запускаем GUI:
    else:
        # Создаём графическое окружение для сервера:
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(database, server, config)

        # Запускаем GUI
        server_app.exec_()

        # По закрытию окон останавливаем обработчик сообщений
        server.running = False


if __name__ == '__main__':
    main()
