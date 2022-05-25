"""Obtain the lemmatize and split a german sentence.

# sentences = nltk.sent_tokenize(text,language='german')

sentences = [elm.strip() for elm in text.splitlines() if elm.strip()]

tokenized_sent = nltk.tokenize.word_tokenize(sentences[23],language='german')
print(tokenized_sent)

pip install git+https://github.com/dtuggener/CharSplit.git
from charsplit import Splitter
splitter = Splitter()
splitter.split_compound("Autobahnraststätte")

splitter.split_compound("Behördenangaben")
# [(1.007164301616347, 'Behörden', 'Angaben'),
# (-0.7395413338811989, 'Behörde', 'Nangaben'),
# (-0.889745566692367, 'Behördenan', 'Gaben'),

slow:  4739 words (words = Path("data/sternstunden04-de.txt").read_text('utf8').split())
%time lemma_data = tagger.tag_sent(words, taglevel=1)
20s

%time spl_data = [split_compound(w) for w in words]
CPU times: total: 656 ms
Wall time: 653 ms

[elm for elm in spl_data if elm[0][0] > .85]

"""
# pylint: disable=invalid-name
import re
import sys
from typing import List, Union
from unicodedata import category

# from charsplit import Splitter
from split_words import Splitter

split_comp = Splitter().split_compound

punctuation = "".join(
    chr(i) for i in range(sys.maxunicode) if category(chr(i)).startswith("P")
)
patt = re.compile(rf"[{re.escape(punctuation)}]")


def split_compound(
    sents_: Union[List[str], str],
) -> List[List[str]]:
    """Lemmatize and split German text."""
    if isinstance(sents_, str):
        sents = [sents_]
    else:
        sents = sents_[:]

    # remove punctuation: replace with " "
    sents = [patt.sub(" ", elm) for elm in sents]

    res = []
    for sent in sents:
        words = sent.split()
        words_ = []
        for word in words:
            # [elm if (split_compound(elm)[0][0] < 0.85) else split_compound(elm)[0][1:] for elm in sent.split()]
            _ = split_comp(word)

            # (0.8640814727771249, 'Regional', 'Gouverneur')
            # logger.debug("lemm: %s, split_compound(lemma)[0]: %s", lemma, _[0])

            if _[0][0] > 0.85:
                words_.extend(_[0][1:])
            else:
                words_.append(word)

        res.append(words_)

    # return [["sein", "Angabe"]]
    return res
