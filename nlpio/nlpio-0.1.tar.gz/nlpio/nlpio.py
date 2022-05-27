import unicodedata
import re
import nltk
import spacy

from bs4 import BeautifulSoup
from nltk.tokenize.toktok import ToktokTokenizer
from nlpio.contractions import CONTRACTION_MAP


def strip_html_tags(text: str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text()
    return stripped_text


def replace_accented_chars(text: str) -> str:
    return (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("utf-8", "ignore")
    )


def remove_special_characters(text: str, remove_digits: bool = False) -> str:
    pattern = r"[^a-zA-Z0-9 ]" if not remove_digits else r"[^a-zA-Z ]"

    return re.sub(pattern, "", text)


def remove_stopwords(
    text: str, is_lower_case: bool = False, words: list[str] = []
) -> str:

    tokenizer = ToktokTokenizer()
    stopwords = nltk.corpus.stopwords.words("english")
    [stopwords.remove(word) for word in words]

    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        tokens = [token for token in tokens if token not in stopwords]
    else:
        tokens = [token for token in tokens if token.lower() not in stopwords]
    return " ".join(tokens)


def expand_contractions(text: str, mapping: dict = CONTRACTION_MAP) -> str:

    contractions_pattern = re.compile(
        "({})".format("|".join(mapping.keys())),
        flags=re.IGNORECASE | re.DOTALL,
    )

    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        expanded_contraction = (
            mapping.get(match)
            if mapping.get(match)
            else mapping.get(match.lower())
        )
        expanded_contraction = first_char + expanded_contraction[1:]
        return expanded_contraction

    expanded_text = contractions_pattern.sub(expand_match, text)
    expanded_text = re.sub("'", "", expanded_text)
    return expanded_text


def lemmatize_text(text: str, vocabulary: str = "en_core_web_sm") -> str:
    spacy_loader = spacy.load(vocabulary)
    text = spacy_loader(text)

    return " ".join(
        [
            word.lemma_ if word.lemma_ != "-PRON-" else word.text for word in text
        ]
    )


def remove_extra_lines(text: str) -> str:
    return re.sub(r"[\r|\n|\r\n]+", " ", text)


def remove_extra_whitespaces(text: str) -> str:
    return re.sub(" +", " ", text)


def clean_corpus(
    corpus: list[str], vocabulary: str = "en_core_web_sm", stopwords: list[str] = []
) -> list:

    normalized_corpus = []

    for doc in corpus:
        doc = doc.lower()
        doc = strip_html_tags(doc)
        doc = expand_contractions(doc)
        doc = replace_accented_chars(doc)
        doc = remove_special_characters(doc)
        doc = remove_extra_lines(doc)
        doc = lemmatize_text(doc, vocabulary)
        doc = remove_stopwords(doc, stopwords)
        doc = remove_extra_whitespaces(doc)

        normalized_corpus.append(doc)

    return normalized_corpus
