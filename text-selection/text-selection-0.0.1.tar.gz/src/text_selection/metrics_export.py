from typing import List, Optional
from typing import OrderedDict as OrderedDictType
from typing import Set, TypeVar

from text_selection.metrics_applied import get_rarity
from text_selection.utils import get_filtered_ngrams

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def get_rarity_ngrams(data: OrderedDictType[int, List[str]], corpus: OrderedDictType[int, List[str]], n_gram: int, ignore_symbols: Optional[Set[str]]) -> OrderedDictType[int, float]:
  data_ngrams = get_filtered_ngrams(data, n_gram, ignore_symbols)
  corpus_ngrams = get_filtered_ngrams(corpus, n_gram, ignore_symbols)
  return get_rarity(
    data=data_ngrams,
    corpus=corpus_ngrams,
  )
