from pathlib import Path
import urllib.request
import pkg_resources


def read_text(filename, encoding='utf8'):
        with open(filename, encoding=encoding) as file:
            return file.read()


def load_list_from_text(filename, encoding='utf8'):
    text = read_text(filename, encoding=encoding)
    return [line for line in text.split('\n')]


def load_capythone_data():
    REV_FILE = pkg_resources.resource_filename('pyembeds', 'data/MyRestaurant_AD_Reviews.txt')
    NEG_FILE = pkg_resources.resource_filename('pyembeds', 'data/negative-words.txt')
    POS_FILE = pkg_resources.resource_filename('pyembeds', 'data/positive-words.txt')
    return {'reviews': load_list_from_text(REV_FILE),'positive_word': load_list_from_text(POS_FILE), 'negative_word': load_list_from_text(NEG_FILE)}

def load_wordcloud_ita_data():
    MANZ_FILE = pkg_resources.resource_filename('pyembeds', 'data/manzoni_1.txt')
    STPW_FILE = pkg_resources.resource_filename('pyembeds', 'data/stopwords_italian.txt')
    return {'manzoni': load_list_from_text(MANZ_FILE), 'stopwords_italian': load_list_from_text(STPW_FILE)}

def donwload_file(url):
    urllib.request.urlretrieve(url, Path(url).name)

def load_list_from_remote(url):
    with urllib.request.urlopen(url) as response:
        text = response.read().decode('utf-8')
        return [line for line in text.split('\n')]