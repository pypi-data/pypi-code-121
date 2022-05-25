from logging import getLogger
from typing import Dict

import numpy as np
from ordered_set import OrderedSet
from text_selection.common.durations_iterator import UntilProxyIterator
from text_selection.common.filter_durations import get_duration_keys
from text_selection.common.mapping_iterator import MappingIterator
from text_selection.random.random_iterator import RandomIterator
from text_selection.utils import DurationBoundary
from tqdm import tqdm


def random_seconds_perf(select_from_keys: OrderedSet[int], select_from_durations_s: Dict[int, float], seconds: float, duration_boundary: DurationBoundary, seed: int) -> OrderedSet[int]:
  logger = getLogger(__name__)

  select_from_keys = get_duration_keys(select_from_durations_s, select_from_keys, duration_boundary)

  kld_iterator = RandomIterator(
    data_indices=OrderedSet(range(len(select_from_keys))),
    seed=seed,
  )

  until_values = np.array([select_from_durations_s[key] for key in select_from_keys])
  until_iterator = UntilProxyIterator(
    iterator=kld_iterator,
    until_values=until_values,
    until_value=seconds,
  )

  key_index_mapping = {index: key for index, key in enumerate(select_from_keys)}
  mapping_iterator = MappingIterator(until_iterator, key_index_mapping)

  result = OrderedSet()
  with tqdm(total=round(seconds), desc="Selected duration", ncols=200, unit="s", position=1) as progress_bar_seconds:
    with tqdm(desc="Iterations", unit="it", position=0) as progress_bar_iterations:
      for item in mapping_iterator:
        result.add(item)
        progress_bar_seconds.update(round(until_iterator.tqdm_update))
        progress_bar_iterations.update()

  if not until_iterator.was_enough_data_available:
    logger.warning("Didn't had enough data!")

  return result
