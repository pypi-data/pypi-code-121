from lib2to3.pgen2.token import STRING
import os
import traceback
import re

from utilities.utilities import get_generic_language, remove_files

STRING_TYPE = 'string'
PLURAL_TYPE = 'plural'


class StringItem:
    
    def __init__(self, key, type, translatable=True, value=None, plural_items=None, comments=None):
        self.key = key
        self.value = value
        self.parsed_value = ""  
        self.placeholder_map = {}
        self.plural_items = plural_items
        self.type = type
        self.translatable = translatable
        self.translated = False
        self.comments = comments
        if type == STRING_TYPE:
            self._parse_value_for_placeholders()

    def _parse_value_for_placeholders(self):
        # not an exaustive parser yet - handles only general use cases, no modifiers
        regex = r'(\%[\d]\$[a-zAZ]|%l[dxui]|%zx|%[a-zAZ]|%[@%])'
        edited_value = self.value
        match = re.search(regex, edited_value)
        index = 0
        while match:
            placeholder = '{' + f'{index}' + '}'
            edited_value = placeholder.join([edited_value[:match.start()], edited_value[match.end():]])
            self.placeholder_map[index] = match.group(0)
            index += 1
            match = re.search(regex, edited_value)
        self.parsed_value = edited_value


class PluralItem:
    def __init__(self, quantity, quantity_value):
        self.quantity = quantity
        self.quantity_value = quantity_value


class StringFile:

    def __init__(self, filepath, language, default=False):
        self.language = language
        self.values = []
        self.filepath = filepath
        self.default = default
        self._read_from_file()

    def _read_from_file(self):
        # print('>>> Reading {}\npath: {}\n'.format(self.language, self.filepath))
        directory = os.path.dirname(self.filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
            with open(self.filepath, "w") as f:
                f.write(self.empty_body)
        self.values = self.parse()
        # print('parsed {} items'.format(len(self.values)))
        # print('\n>>> Closing {}\n\n'.format(self.language))

    @property
    def header(self):
        raise NotImplementedError("header must be implemented")

    @property
    def body(self):
        raise NotImplementedError("body must be implemented")

    @property
    def footer(self):
        raise NotImplementedError("footer must be implemented")

    @property
    def empty_body(self):
        return f'{self.header}\n{self.footer}'

    def parse(self):
        raise NotImplementedError("parse must be implemented")

    @staticmethod
    def get_string_files(config):
        raise NotImplementedError('get_string_files must be implemented')

    @property
    def generic_language(self):
        return get_generic_language(self.language)

    @staticmethod
    def popuplate_with_new_keys(config):
        raise NotImplementedError("popuplate_with_new_keys must be implemented")

    def insert_new_string_key(self, key, default_value=""):
        self.values.append(
            StringItem(
                key,
                STRING_TYPE,
                translatable=True,
                value=default_value,
            )
        )

    def update_values(self, map):
        has_changes = False
        for value in list(filter(lambda v: v.translatable and v.type == STRING_TYPE, self.values)):
            string_index = list(filter(lambda o: value.key in [k.key for k in o.keys], map.index.values()))[0]
            string_value = string_index.translations[self.generic_language]
            string_key = next(filter(lambda k: value.key == k.key, string_index.keys))
            for index, placeholder in string_key.placeholder_map.items():
                string_value = string_value.replace('{' + f'{index}' + '}', placeholder)
            if string_value and string_value != value.value:
                value.value = string_value
                has_changes = True
        
        if has_changes:
            self.update_strings_file()

    def update_strings_file(self):
        try:
            original = self.filepath
            old = original + '.old'
            new = original + '.new'
            if os.path.isfile(original):
                self.save_to_file(new)
                os.rename(original, old)
                os.rename(new, original)
                remove_files([old, new])
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    def save_to_file(self, path):
        with open(path, 'w') as f:
            f.write(f'{self.header}{self.body}{self.footer}')
