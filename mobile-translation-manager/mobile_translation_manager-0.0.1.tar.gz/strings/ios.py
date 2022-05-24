
import os
from re import compile
from strings.strings import STRING_TYPE, StringFile, StringItem

re_translation = compile(r'^"(.*)" = "(.*)";$')
re_comment_single = compile(r'^/\*.*\*/$')
re_comment_start = compile(r'^/\*.*$')
re_comment_end = compile(r'^.*\*/$')


class iOSStringFile(StringFile):
    
    @property
    def header(self):
        return ""

    @property
    def body(self):
        body_string = ""
        sorted_values = sorted(self.values, key=lambda x: x.key.lower())
        for value in sorted_values:
            comments = "/* No comment provided by engineer. */"
            if len(value.comments) > 0:
                comments = ""
                for comment in value.comments:
                    comments += f'{comment}'

            # if blank we need to get the default value from the default language file and set this field
            body_string += f'{comments}"{value.key}" = "{value.value if value.value else value.key}";\n\n'
        return body_string

    @property
    def footer(self):
        return ""

    def parse(self):
        string_items = []
        with open(self.filepath, 'r') as f:
            line = f.readline()
            while line:
                comments = [line]
                if not re_comment_single.match(line):
                    while line and not re_comment_end.match(line):
                        line = f.readline()
                        comments.append(line)
                
                line = f.readline()
                if line and re_translation.match(line):
                    translation = line
                else:
                    continue
                
                line = f.readline()
                while line and line == u'\n':
                    line = f.readline()

                key, value = re_translation.match(translation).groups()
                string_items.append(
                    StringItem(
                        key,
                        STRING_TYPE,
                        value=value,
                        comments=comments
                    )
                )

        return string_items

    @staticmethod
    def get_string_files(config):
        string_files = []
        for string_dir in config.string_dirs:
            for language in config.languages:
                path = os.path.normpath(f'{config.project_dir}/{string_dir}/{language}.lproj/{config.strings_filename}')
                string_files.append(iOSStringFile(path, language, default=language == config.default_language))
        return string_files

    @staticmethod
    def popuplate_with_new_keys(config):
        pass
