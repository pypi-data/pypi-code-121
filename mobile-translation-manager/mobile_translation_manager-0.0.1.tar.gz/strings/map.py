from marshmallow import Schema, fields, post_load

from strings.strings import STRING_TYPE


FUZZY = "~fuzzy; "

class StringKeySchema(Schema):
    key = fields.Str()
    placeholder_map = fields.Dict(keys=fields.Int(), values=fields.Str())

    @post_load
    def make_string_key(self, data, **__):
        return StringKey(**data)


class StringKey:

    def __init__(self, key, placeholder_map):
        self.key = key
        self.placeholder_map = placeholder_map


class StringIndexSchema(Schema):
    value = fields.Str()
    type = fields.Str()
    translatable = fields.Bool()
    keys = fields.List(fields.Nested(StringKeySchema()))
    translations = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make_string_index(self, data, **__):
        return StringIndex(**data)


class StringIndex:

    def __init__(self, value, type, key=None, placeholder_map=None, languages=None, translatable=True, translations=None, keys=None):
        self.value = value
        self.type = type
        self.translatable = translatable
        if translations and keys:
            self.keys = keys
            self.translations = translations
        else:
            self.keys = [
                StringKey(
                    key,
                    placeholder_map
                )
            ]
            self.translations = { language: "" for language in languages } if languages else {}
    

class StringsMapSchema(Schema):
    index = fields.Dict(keys=fields.Str(), values=fields.Nested(StringIndexSchema()))

    @post_load
    def make_strings_map(self, data, **__):
        return StringsMap(**data)

class StringsMap:
    # only string types supported at the moment
    
    def __init__(self, string_files=None, languages=None, index=None):
        if string_files and languages:
            self.index = {}
            self._map(string_files, languages)
        else:
            self.index = index

    def _map(self, string_files, languages):
        def find_index_by_key(key):
            for index in self.index.values():
                if key in [k.key for k in index.keys]:
                    return index

        def update_index(key, language, value):
            for index in self.index.values():
                if key in [k.key for k in index.keys]:
                    index.translations[language] = value

        default_files = list(filter(lambda d: d.default == True, string_files))
        for default_file in default_files:
            for string_item in list(filter(lambda s: s.type == STRING_TYPE and s.translatable, default_file.values)):
                if string_item.parsed_value in self.index:
                    self.index[string_item.parsed_value].keys.append(
                        StringKey(
                            string_item.key,
                            string_item.placeholder_map
                        )
                    )
                else:
                    self.index[string_item.parsed_value] = StringIndex(
                        string_item.parsed_value,
                        STRING_TYPE,
                        string_item.key,
                        string_item.placeholder_map,
                        languages,
                        string_item.translatable
                    )

        translation_files = list(filter(lambda d: d.default == False, string_files))
        for translation_file in translation_files:
            for string_item in list(filter(lambda s: s.type == STRING_TYPE and s.translatable, translation_file.values)):
                index = find_index_by_key(string_item.key)
                try:
                    raw_value = index.value
                except Exception:
                    print(f'error with value: {string_item.key} - {translation_file.language}\npath: {translation_file.filepath}')
                    exit(1)
                translated_value = index.translations.get(translation_file.generic_language, raw_value)
                if translated_value and string_item.parsed_value != raw_value:
                    if FUZZY in translated_value:
                        conflicts = translated_value.replace(FUZZY, "").split('|')
                        if string_item.parsed_value not in conflicts:
                            # print("adding conflict")
                            conflicts.append(string_item.parsed_value)
                            new_value = f'{FUZZY}{"|".join(conflicts)}'
                            update_index(string_item.key, translation_file.generic_language, new_value)
                    elif raw_value != translated_value and translated_value != string_item.parsed_value:
                        # print(f'conflicting translation for {translation_file.language}:\n\tkey: "{raw_value}"\n\ttranslation: "{translated_value}"\n\tconflict: "{string_item.parsed_value}"\nmarked as fuzzy\n\n')
                        update_index(string_item.key, translation_file.generic_language, f'{FUZZY}{translated_value}|{string_item.parsed_value}')
                    elif raw_value == translated_value and string_item.parsed_value not in [translated_value, raw_value]:
                        update_index(string_item.key, translation_file.generic_language, string_item.parsed_value)
                elif string_item.parsed_value:
                    update_index(string_item.key, translation_file.generic_language, string_item.parsed_value)

    def update_files(self, string_files=None):
        has_fuzzy = next(filter(lambda i: next(filter(lambda v: FUZZY in v, i.translations.values()), None) is not None, self.index.values()), None)
        if has_fuzzy:
            print("!!! you must resolve fuzzy translations before saving !!!")
            exit(1)

        if string_files:
            self.string_files = string_files
        
        for string_file in self.string_files:
            string_file.update_values(self)

    def update(self, key, language, translation):
        string_index = self.index[key]
        translated_value = string_index.translations[language]
        translation = translation if translation else key
        if FUZZY in translated_value:
            conflicts = translated_value.replace(FUZZY, "").split('|')
            if translation not in conflicts:
                # print("adding conflict")
                conflicts.append(translation)
                new_value = f'{FUZZY}{"|".join(conflicts)}'
                string_index.translations[language] = new_value
        elif not translated_value:
            string_index.translations[language] = translation
        elif key != translated_value and translated_value != translation:
            # print(f'conflicting translation for {language}:\n\tkey: "{key}"\n\ttranslation: "{translated_value}"\n\tconflict: "{translation}"\nmarked as fuzzy\n\n')
            string_index.translations[language] = f'{FUZZY}{translated_value}|{translation}'
        elif key == translated_value and translation not in [translated_value, key]:
            string_index.translations[language] = new_value
