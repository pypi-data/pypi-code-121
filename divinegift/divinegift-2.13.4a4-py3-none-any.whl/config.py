from typing import Union, Optional

from cryptography.fernet import InvalidToken

from divinegift import main
from divinegift import logger
from divinegift import cipher
#########################################################################
import sys
import os
from datetime import datetime
from copy import deepcopy

from divinegift.errors import EmptyConfigError, ConfigNotFoundError


class Settings:
    parse_settings_cnt = 0

    def __init__(self, file_: Optional[str] = None, ck_fname: Optional[str] = 'key.ck', encoding: str = 'utf-8',
                 log_changes: bool = False, use_yaml: bool = True, ignore_parse_cnt: bool = True,
                 logger_: logger.Logger = None):
        self.settings: dict = {}
        self.settings_encrypted: dict = {}
        self.encrypted_values: dict = {}
        self.cipher_key = None
        self.cipher_key_fname = None
        self.passwords_cnt = 0
        self.logger = logger_ if logger_ else logger.Logger()

        self.file_extensions_allowed = ['json', 'yaml', 'yml', 'ini', 'cfg', 'conf']

        if file_:
            self.parse_settings(file_, ck_fname, encoding, log_changes, use_yaml, ignore_parse_cnt)

    def get_settings(self, param: str = None, default: Union[str, list, dict, bool] = None):
        if param:
            return self.settings.get(param, default)
        return self.settings

    def set_settings(self, json_str: dict):
        self.settings = deepcopy(json_str)
        if self.cipher_key_fname:
            self.decrypt_passwords()
        self.settings_encrypted = deepcopy(json_str)

    def decrypt_passwords(self):
        self.logger.log_debug('Try to decrypt all passwords')
        for conn_name in self.settings.keys():
            try:
                for pass_field in self.settings.get(conn_name).keys():
                    try:
                        self.decrypt_password(conn_name, pass_field)
                        self.logger.log_debug(f'Password for {conn_name}[{pass_field}] decrypted')
                        self.passwords_cnt += 1
                        self.encrypted_values[conn_name] = pass_field
                    except:
                        pass
            except:
                pass

    def find_config_file(self, file):
        d, f = os.path.split(file)
        for ext in self.file_extensions_allowed:
            f_n = f.replace(main.get_file_extension(f), '') + f'.{ext}'
            if os.path.exists(os.path.join(d, f_n)):
                self.logger.log_info(f'Found config file with extension: {f_n}')
                return os.path.join(d, f_n)
        raise ConfigNotFoundError(f'There is no config file in directory {d} with allowed extensions: [{self.file_extensions_allowed}]')

    def parse_settings(self, file_: str = './settings.yaml', ck_fname: str = 'key.ck', encoding: str = 'utf-8',
                       log_changes: bool = False, use_yaml: bool = True, ignore_parse_cnt: bool = True):
        """
        Parse settings from file_
        :param file_: Filename with settings
        :param ck_fname: Filename with key.ck
        :param encoding: Encoding
        :param log_changes: Set to False for not showing logs of parsing configs
        :param use_yaml: True by default. Set to False if settings in JSON
        :param ignore_parse_cnt: Set to False if repeatedly reads configs
        :return: None
        """
        if not ignore_parse_cnt:
            self.__class__.parse_settings_cnt += 1
            if self.__class__.parse_settings_cnt > 2:
                raise EmptyConfigError('Settings not parsed. Is there any data?')

        if not os.path.exists(file_):
            file_ = self.find_config_file(file_)
        
        if use_yaml:
            c = main.Yaml(file_, encoding=encoding)
        else:
            c = main.Json(file_, encoding=encoding)

        json_data = c.parse()

        if log_changes and json_data:
            dict_c = main.dict_compare(self.settings_encrypted, json_data)
            added, removed, modified, same = dict_c.values()
            if len(added) > 0:
                for r in list(added):
                    self.logger.log_warn(f'Added {r}: {json_data.get(r)}')
            if len(removed) > 0:
                for r in list(removed):
                    self.logger.log_warn(f'Removed {r}: {self.settings_encrypted.get(r)}')
            if len(modified) > 0:
                for r in list(modified):
                    self.logger.log_warn(f'Modified {r}: {modified.get(r)[0]} -> {modified.get(r)[1]}')
        elif not json_data:
            try:
                # self.convert_config(file_, file_, encoding=encoding, use_yaml=use_yaml)
                self.parse_settings(file_, encoding, ck_fname, not use_yaml)
            except EmptyConfigError as ms:
                self.logger.log_err(ms)
                sys.exit(-1)
            except Exception as ex:
                raise Exception('Settings not parsed. Is there any data 2?')

        self.cipher_key_fname = ck_fname

        self.set_settings(json_data)

    def initialize_cipher(self, ck_fname: str = 'key.ck'):
        self.cipher_key = cipher.get_key()
        cipher.write_key(ck_fname, self.cipher_key)

    def encrypt_password(self, encrypt_field: str, encrypt_value: str = 'db_pass'):
        if not self.cipher_key:
            self.cipher_key = cipher.read_key(self.cipher_key_fname)
            if not self.cipher_key:
                self.initialize_cipher()
        cipher_ = cipher.get_cipher(self.cipher_key)
        self.settings[encrypt_field][encrypt_value] = cipher.encrypt_str(self.settings[encrypt_field][encrypt_value], cipher_)

    def decrypt_password(self, encrypt_field: str, encrypt_value: str = 'db_pass'):
        if not self.cipher_key:
            self.cipher_key = cipher.read_key(self.cipher_key_fname)
        cipher_ = cipher.get_cipher(self.cipher_key)
        self.settings[encrypt_field][encrypt_value] = cipher.decrypt_str(self.settings[encrypt_field][encrypt_value], cipher_)

    def encode_password(self, encrypt_field: str, encrypt_value: str = 'db_pass'):
        settings = self.get_settings().copy()
        settings[encrypt_field][encrypt_value] = cipher.encode_password(settings[encrypt_field][encrypt_value])
        self.set_settings(settings)

    def decode_password(self, encrypt_field: str, encrypt_value: str = 'db_pass'):
        settings = self.get_settings().copy()
        settings[encrypt_field][encrypt_value] = cipher.decode_password(settings[encrypt_field][encrypt_value])
        self.set_settings(settings)

    def save_settings(self, file_: str = './settings.yml', encoding='utf-8', use_yaml=True):
        if use_yaml:
            c = main.Yaml(file_, encoding=encoding)
        else:
            c = main.Json(file_, encoding=encoding)
        c.set_data(eval(str(self.get_settings())))
        c.create()

    def check_config_still_encrypted(self):
        for encrypted_field, encrypted_value in self.encrypted_values.items():
            try:
                cipher_ = cipher.get_cipher(self.cipher_key)
                cipher.decrypt_str(self.settings[encrypted_field][encrypted_value], cipher_)
            except InvalidToken:
                self.encrypt_password(encrypted_field, encrypted_value)

    @staticmethod
    def convert_config(file_from: str = './settings.yml', file_to: str = './settings.yml',
                       encoding='utf-8', use_yaml=True):
        if use_yaml:
            j = main.Json(file_from, encoding=encoding)
            y = main.Yaml(file_to, encoding=encoding)
            j.parse()
            y.set_data(j.get_data())
            y.create()
        else:
            y = main.Yaml(file_from, encoding=encoding)
            j = main.Json(file_to, encoding=encoding)
            y.parse()
            j.set_data(y.get_data())
            j.create()

    @staticmethod
    def get_version(fname=None):
        if not fname:
            fname = sys.argv[0]
        filename = main.get_list_files(os.path.dirname(fname), filter=os.path.basename(fname), add_path=True)[-1]
        version = datetime.fromtimestamp(os.path.getmtime(filename))
        return datetime.strftime(version, '%y%m%d')


if __name__ == '__main__':
    pass
