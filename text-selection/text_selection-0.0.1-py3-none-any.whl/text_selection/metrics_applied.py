from typing import List
from typing import OrderedDict as OrderedDictType
from typing import TypeVar

from text_selection.metrics_methods import get_rarity_data
from text_selection.utils import get_distribution

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def get_rarity(data: OrderedDictType[_T1, List[_T2]], corpus: OrderedDictType[_T1, List[_T2]]) -> OrderedDictType[_T1, float]:
  corpus_distr = get_distribution(corpus)
  rarity_data = get_rarity_data(
    data=data,
    distribution=corpus_distr,
  )

  return rarity_data
