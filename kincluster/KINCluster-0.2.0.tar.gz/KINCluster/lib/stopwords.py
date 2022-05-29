import codecs
from pathlib import Path



def __get_stopwords():
    stopwords_dir = Path(__file__).parent.joinpath('stopwords')
    words = set()
    for file_name in stopwords_dir.iterdir():
        with codecs.open(str(file_name), 'r', encoding='utf-8') as f:
            ctx = f.readlines()
        words.update(map(str.strip, ctx))
    return words


stopwords = list(__get_stopwords())
