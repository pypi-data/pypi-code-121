import binascii
import hashlib
import hmac
import socket
import sys
import time
import json
import threading
from server.common.errors import ServerError
from server.common.variables import *
from server.common.utils import get_message, send_message
from server.common.errors import IncorrectDataRecivedError

from PyQt5.QtCore import pyqtSignal, QObject

sys.path.append('../../messenger/')

# Логгер и объект блокировки для работы с сокетом.
CLIENT_LOGGER = logging.getLogger('client')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    """
    Класс реализующий транспортную подсистему клиентского
    модуля. Отвечает за взаимодействие с сервером.
    """
    # Сигналы новое сообщение и потеря соединения
    new_message = pyqtSignal(dict)
    message_205 = pyqtSignal()
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username, passwd, keys):
        # Вызываем конструкторы предков
        threading.Thread.__init__(self)
        QObject.__init__(self)

        # Класс База данных - работа с базой
        self.database = database
        # Имя пользователя
        self.username = username
        # Пароль
        self.password = passwd
        # Сокет для работы с сервером
        self.transport = None
        # Набор ключей для шифрования
        self.keys = keys
        # Устанавливаем соединение:
        self.connection_init(port, ip_address)
        # Обновляем таблицы известных пользователей и контактов
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            CLIENT_LOGGER.error(
                'Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
            # Флаг продолжения работы транспорта.
        self.running = True

    def connection_init(self, port, ip):
        """Метод отвечающий за установку соединения с сервером."""
        # Инициализация сокета и сообщение серверу о нашем появлении
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Таймаут необходим для освобождения сокета.
        self.transport.settimeout(5)

        # Соединяемся, 5 попыток соединения, флаг успеха ставим в True, если
        # удалось
        connected = False
        for i in range(5):
            CLIENT_LOGGER.info(f'Попытка подключения №{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                CLIENT_LOGGER.debug("Connection established.")
                break
            time.sleep(1)

        # Если соединиться не удалось - исключение
        if not connected:
            CLIENT_LOGGER.critical(
                'Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')

        CLIENT_LOGGER.debug('Установлено соединение с сервером')

        CLIENT_LOGGER.debug('Starting auth dialog.')

        # Запускаем процедуру авторизации.
        # Получаем хэш пароля
        passwd_bytes = self.password.encode('utf-8')
        salt = self.username.lower().encode('utf-8')
        passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
        passwd_hash_string = binascii.hexlify(passwd_hash)

        CLIENT_LOGGER.debug(f'Passwd hash ready: {passwd_hash_string}')

        # Получаем публичный ключ и декодируем его из байтов
        pubkey = self.keys.publickey().export_key().decode('ascii')

        # Авторизуемся на сервере
        with socket_lock:
            presence = {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: self.username,
                    PUBLIC_KEY: pubkey
                }
            }
            CLIENT_LOGGER.debug(f"Presence message = {presence}")
            # Отправляем серверу приветственное сообщение.
            try:
                send_message(self.transport, presence)
                ans = get_message(self.transport)
                CLIENT_LOGGER.debug(f'Server response = {ans}.')
                # Если сервер вернул ошибку, бросаем исключение.
                if RESPONSE in ans:
                    if ans[RESPONSE] == 400:
                        raise ServerError(ans[ERROR])
                    elif ans[RESPONSE] == 511:
                        # Если всё нормально, то продолжаем процедуру
                        # авторизации.
                        ans_data = ans[DATA]
                        hash = hmac.new(
                            passwd_hash_string,
                            ans_data.encode('utf-8'),
                            'MD5')
                        digest = hash.digest()
                        my_ans = RESPONSE_511
                        my_ans[DATA] = binascii.b2a_base64(
                            digest).decode('ascii')
                        send_message(self.transport, my_ans)
                        self.process_ans(get_message(self.transport))
            except (OSError, json.JSONDecodeError) as err:
                CLIENT_LOGGER.debug(f'Connection error.', exc_info=err)
                raise ServerError('Сбой соединения в процессе авторизации.')

    def process_ans(self, message):
        """Метод обработчик поступающих сообщений с сервера."""
        CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')

        # Если это подтверждение чего-либо
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.user_list_update()
                self.contacts_list_update()
                self.message_205.emit()
            else:
                CLIENT_LOGGER.error(
                    f'Принят неизвестный код подтверждения '
                    f'{message[RESPONSE]}')

        # Если это сообщение от пользователя добавляем в базу, даём сигнал о
        # новом сообщении
        elif ACTION in message and message[ACTION] == MESSAGE \
                and SENDER in message and TARGET in message \
                and MESSAGE_TEXT in message \
                and message[TARGET] == self.username:
            CLIENT_LOGGER.debug(
                f'Получено сообщение от пользователя '
                f'{message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.new_message.emit(message)

    def contacts_list_update(self):
        """Метод обновляющий с сервера список контактов."""
        self.database.contacts_clear()
        CLIENT_LOGGER.debug(
            f'Запрос контакт листа для пользователя {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        CLIENT_LOGGER.debug(f'Сформирован запрос {req}')
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        CLIENT_LOGGER.debug(f'Получен ответ {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            CLIENT_LOGGER.error('Не удалось обновить список контактов.')

    def user_list_update(self):
        """Метод обновляющий с сервера список пользователей"""
        CLIENT_LOGGER.debug(
            f'Запрос списка известных пользователей {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            CLIENT_LOGGER.error(
                'Не удалось обновить список известных пользователей.')

    def key_request(self, user):
        """Метод запрашивающий с сервера публичный ключ пользователя."""
        CLIENT_LOGGER.debug(f'Запрос публичного ключа для {user}')
        req = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 511:
            return ans[DATA]
        else:
            CLIENT_LOGGER.error(f'Не удалось получить ключ собеседника{user}.')

    def add_contact(self, contact):
        """Метод отправляющий на сервер сведения о добавлении контакта."""
        CLIENT_LOGGER.debug(f'Создание контакта {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_ans(get_message(self.transport))

    def remove_contact(self, contact):
        """Метод отправляющий на сервер сведения об удалении контакта."""
        CLIENT_LOGGER.debug(f'Удаление контакта {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_ans(get_message(self.transport))

    def transport_shutdown(self):
        """Метод уведомляющий сервер о завершении работы клиента."""
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                pass
        CLIENT_LOGGER.debug('Транспорт завершает работу.')
        time.sleep(0.5)

    def send_message(self, to, message):
        """Метод отправляющий на сервер сообщения для пользователя."""
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            TARGET: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_ans(get_message(self.transport))
            CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to}')

    def run(self):
        """Метод содержащий основной цикл работы транспортного потока."""
        CLIENT_LOGGER.debug('Запущен процесс - приёмник сообщений с сервера.')
        while self.running:
            # Отдыхаем секунду и снова пробуем захватить сокет.
            # если не сделать тут задержку, то отправка может достаточно долго
            # ждать освобождения сокета.
            time.sleep(1)
            message = None
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                    # Принято некорректное сообщение
                except IncorrectDataRecivedError:
                    CLIENT_LOGGER.error(
                        f'Не удалось декодировать полученное сообщение.')
                # Вышел таймаут соединения, если errno = None, иначе обрыв
                # соединения.
                except OSError as err:
                    if err.errno:
                        CLIENT_LOGGER.critical(
                            f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError, TypeError):
                    CLIENT_LOGGER.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                finally:
                    self.transport.settimeout(5)

            # Если сообщение получено, то вызываем функцию обработчик:
            if message:
                CLIENT_LOGGER.debug(f'Принято сообщение с сервера: {message}')
                self.process_ans(message)
