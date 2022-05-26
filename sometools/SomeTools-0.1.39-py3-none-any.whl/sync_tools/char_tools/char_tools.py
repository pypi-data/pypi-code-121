import chardet
from sometools.sync_tools.base import Base


class CharMixin(Base):
    """
    https://chardet.readthedocs.io/en/latest/supported-encodings.html
    """

    def __init__(self, *args, **kwargs):
        super(CharMixin, self).__init__(*args, **kwargs)

    @staticmethod
    def char_detect(bytes_content: bytes) -> dict:
        return chardet.detect(bytes_content)

    @staticmethod
    def char_to_str(bytes_content: bytes) -> str:
        encoding_dict = CharMixin.char_detect(bytes_content)  # <class 'dict'>: {'encoding': 'utf-8', 'confidence': 0.99, 'language': ''}
        if len(bytes_content) >= 52428800:
            raise Exception('error: char length >= 50MB')
        if encoding_dict.get('confidence') > 0.5:
            return bytes_content.decode(encoding=encoding_dict.get('encoding'))
        raise Exception('error: confidence <= 0.5')