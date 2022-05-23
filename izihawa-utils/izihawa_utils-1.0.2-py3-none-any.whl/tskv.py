MAX_LOG_LENGTH = 8192
REPLACE_MAP = [
    ('\\', r'\\'),
    ('\t', r'\t'),
    ('\n', r'\n'),
    ('\r', r'\r'),
    ('\0', r'\0'),
]


class TskvRecord(dict):
    preferred_fields = ['unixtime', 'datetime', 'request_id', 'user_ip', 'path']

    @staticmethod
    def escape_value(text):
        for char, replacement in REPLACE_MAP:
            text = text.replace(char, replacement)
        return text

    @staticmethod
    def truncate_str(text):
        return text[:MAX_LOG_LENGTH]

    def __str__(self):
        elements = []
        for preferred_field in self.preferred_fields:
            if self.get(preferred_field) is not None:
                elements.append(self.escape_value('%s=%s' % (preferred_field, self[preferred_field])))
                self.pop(preferred_field)
        for k, v in sorted(self.items()):
            if v is not None:
                elements.append(self.escape_value('%s=%s' % (k, v)))
        return self.truncate_str('\t'.join(elements))
