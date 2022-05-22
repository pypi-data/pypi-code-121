"""Программа-клиент"""
import os
import argparse
import sys

from Cryptodome.PublicKey import RSA

from PyQt5.QtWidgets import QApplication, QMessageBox

from server.common.errors import ServerError
from server.common import log
from client.client_dir.client_database import ClientDatabase
from client.client_dir import ClientTransport
from client.client_dir.main_window import ClientMainWindow
from client.client_dir import UserNameDialog

# Инициализация клиентского логгера
CLIENT_LOGGER = logging.getLogger('client')


# Парсер аргументов командной строки
@log
def arg_parser():
    """
    Парсер аргументов командной строки, возвращает кортеж из 4 элементов
    адрес сервера, порт, имя пользователя, пароль.
    Выполняет проверку на корректность номера порта.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_passwd = namespace.password

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером '
            f'порта: {server_port}. Допустимы адреса с 1024 до 65535. '
            f'Клиент завершается.')
        sys.exit(1)

    return server_address, server_port, client_name, client_passwd


if __name__ == '__main__':
    """Основная функция клиента"""
    # Загружаем параметры командной строки
    server_address, server_port, client_name, client_passwd = arg_parser()
    CLIENT_LOGGER.debug('Args loaded')

    # Создаём клиентское приложение
    client_app = QApplication(sys.argv)

    # Если имя пользователя не было указано в командной строке, то запросим его
    start_dialog = UserNameDialog()
    if not client_name:
        client_app.exec_()
        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое
        # и удаляем объект, иначе выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_passwd = start_dialog.client_passwd.text()
            CLIENT_LOGGER.debug(
                f'Using USERNAME = {client_name}, PASSWD = {client_passwd}.')
            # del start_dialog
        else:
            sys.exit(0)

    # Записываем логи
    CLIENT_LOGGER.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address}, '
        f'порт: {server_port}, '
        f'имя пользователя: {client_name}')

    # Загружаем ключи с файла, если же файла нет, то генерируем новую пару.
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.getcwd()
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    # !!!keys.publickey().export_key()
    CLIENT_LOGGER.debug("Keys successfully loaded.")

    # Создаём объект базы данных
    database = ClientDatabase(client_name)

    # Создаём объект - транспорт и запускаем транспортный поток
    try:
        transport = ClientTransport(
            server_port,
            server_address,
            database,
            client_name,
            client_passwd,
            keys)
        CLIENT_LOGGER.debug("Transport ready.")
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Ошибка сервера', error.text)
        sys.exit(1)

    transport.setDaemon(True)
    transport.start()

    # Удалим объект диалога за ненадобностью
    del start_dialog

    # Создаём GUI
    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    # Раз графическая оболочка закрылась, закрываем транспорт
    transport.transport_shutdown()
    transport.join()
